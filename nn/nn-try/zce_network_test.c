/*
 * zce_network_test.c
 * ==================
 * Rigorous end-to-end test: Python-encoded ZCE streams → C decoder → predictions.
 *
 * Tests:
 *   1. Iris      (4-in, 16-hidden, 3-class)   — numpy acc 1.000
 *   2. Moons     (2-in,  8-hidden, 2-class)   — numpy acc 0.800
 *   3. Blobs     (4-in, 12-hidden, 4-class)   — numpy acc 1.000
 *
 * For each network, for each sample:
 *   - Run ZCE stream through C decoder
 *   - Compare prediction in slot[50+i] vs numpy prediction
 *   - Report per-sample pass/fail + accuracy
 *
 * A PASS means the C decoder agrees with the numpy reference exactly.
 * Any discrepancy in any sample fails the test.
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

/* Frozen decoder first (defines ZCEDecoder) */
#include "zce_decoder.h"
/* ML extended executor (uses ZCEDecoder) */
#include "zce_ml_exec.h"
/* Embedded test streams */
#include "zce_test_streams.h"

/* ── Test result struct ─────────────────────────────────── */

typedef struct {
    const char *name;
    int n_samples;
    int n_match;          /* C == numpy */
    int n_numpy_correct;  /* numpy == true label */
    int n_c_correct;      /* C == true label */
    double elapsed_ms;
    int error;
    char errmsg[256];
} TestResult;

/* ── Run one network's full stream ──────────────────────── */

TestResult run_network_test(
    const char     *name,
    const uint8_t  *stream,
    int             stream_len,
    const int      *np_preds,
    const int      *true_labels,
    int             n_samples)
{
    TestResult r = {0};
    r.name      = name;
    r.n_samples = n_samples;

    printf("\n[%s] stream=%d bytes, %d samples\n", name, stream_len, n_samples);

    /* Reset array pool between networks */
    zce_arrays_reset();

    /* Time the decode */
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    ZCEDecoder d;
    zce_init(&d, stream, stream_len);
    d.exec_ext = zce_ml_exec;

    int ok = zce_run(&d);

    clock_gettime(CLOCK_MONOTONIC, &t1);
    r.elapsed_ms = ((t1.tv_sec - t0.tv_sec) * 1e3) +
                   ((t1.tv_nsec - t0.tv_nsec) / 1e6);

    if (ok != 0) {
        r.error = 1;
        snprintf(r.errmsg, sizeof r.errmsg, "%s", d.errmsg);
        printf("  ERROR: %s\n", d.errmsg);
        return r;
    }

    printf("  Executed in %.2f ms, %d steps\n", r.elapsed_ms, d.steps);
    printf("  %-6s  %-8s  %-8s  %-6s  %-6s\n",
           "Sample", "C pred", "NP pred", "True", "Match");
    printf("  %s\n", "----------------------------------------------");

    for (int i = 0; i < n_samples; i++) {
        int c_pred = (int)zce_slot(&d, 50 + i);
        int np_pred = np_preds[i];
        int true_lbl = true_labels[i];
        int match = (c_pred == np_pred);
        int c_correct  = (c_pred  == true_lbl);
        int np_correct = (np_pred == true_lbl);

        r.n_match        += match;
        r.n_c_correct    += c_correct;
        r.n_numpy_correct += np_correct;

        const char *mark = match ? "✓" : "✗ MISMATCH";
        printf("  [%2d]    %-8d %-8d %-6d %s\n",
               i, c_pred, np_pred, true_lbl, mark);
    }

    printf("\n  C==numpy:    %d/%d  (%.1f%%)\n",
           r.n_match, n_samples, 100.0 * r.n_match / n_samples);
    printf("  C accuracy:  %d/%d  (%.1f%%)\n",
           r.n_c_correct, n_samples, 100.0 * r.n_c_correct / n_samples);
    printf("  NP accuracy: %d/%d  (%.1f%%)\n",
           r.n_numpy_correct, n_samples, 100.0 * r.n_numpy_correct / n_samples);

    return r;
}

/* ── Mismatch test: what if we swap the activation? ─────── */
/*
 * From exp-3: tanh→leaky_relu drops 53 points on Moons.
 * We prove the same thing here: run the Moons stream but
 * provide an exec_ext that uses tanh instead of leaky_relu.
 * The grammar section (DEFINE_OP) says leaky_relu — so if we
 * swap the executor, predictions must change.
 *
 * This is the key insight: the stream *declares* its ops by
 * name (action_param code). The executor implements them.
 * If they don't match, the model breaks.
 */

static void wrong_exec(ZCEDecoder *d, int param, int64_t *args) {
    /* Everything same as zce_ml_exec except LEAKY_RELU (44) → tanh */
    if (param == 44) {
        /* Wrong: apply tanh instead of leaky_relu */
        int arr_id = (int)d->slots[args[0]];
        int n      = (int)d->slots[args[1]];
        for (int i = 0; i < n; i++) {
            float v = zce_arr_get(arr_id, i);
            zce_arr_set(arr_id, i, tanhf(v));
        }
    } else {
        zce_ml_exec(d, param, args);
    }
}

void run_mismatch_test(void) {
    printf("\n[MISMATCH TEST: Moons with tanh instead of leaky_relu]\n");
    printf("  (Proves the stream encodes which activation to use)\n\n");

    const uint8_t *stream = ZCE_STREAM_MOONS;
    int len               = ZCE_STREAM_MOONS_LEN;
    int n                 = ZCE_NSAMPLES_MOONS;

    zce_arrays_reset();

    ZCEDecoder d_correct, d_wrong;

    zce_init(&d_correct, stream, len);
    d_correct.exec_ext = zce_ml_exec;
    zce_run(&d_correct);

    zce_arrays_reset();
    zce_init(&d_wrong, stream, len);
    d_wrong.exec_ext = wrong_exec;
    zce_run(&d_wrong);

    int agree = 0, correct_correct = 0, wrong_correct = 0;
    for (int i = 0; i < n; i++) {
        int c = (int)zce_slot(&d_correct, 50 + i);
        int w = (int)zce_slot(&d_wrong,   50 + i);
        int t = ZCE_TRUE_MOONS[i];
        agree          += (c == w);
        correct_correct += (c == t);
        wrong_correct   += (w == t);
    }

    printf("  Correct executor accuracy: %d/%d (%.1f%%)\n",
           correct_correct, n, 100.0 * correct_correct / n);
    printf("  Wrong executor accuracy:   %d/%d (%.1f%%)\n",
           wrong_correct, n, 100.0 * wrong_correct / n);
    printf("  Predictions agree:         %d/%d\n", agree, n);
    int drop = correct_correct - wrong_correct;
    printf("  Accuracy drop (leaky→tanh): %d points\n", drop);
    if (drop > 0)
        printf("  ✓ Activation swap changes predictions — grammar carries meaning\n");
    else
        printf("  ✗ Activation swap had no effect (unexpected)\n");
}

/* ── Timing benchmark ───────────────────────────────────── */

void run_timing_benchmark(void) {
    printf("\n[TIMING BENCHMARK]\n");
    printf("  Repeated Iris decode × 100 runs\n");

    int N = 100;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (int r = 0; r < N; r++) {
        zce_arrays_reset();
        ZCEDecoder d;
        zce_init(&d, ZCE_STREAM_IRIS, ZCE_STREAM_IRIS_LEN);
        d.exec_ext = zce_ml_exec;
        zce_run(&d);
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double total_ms = ((t1.tv_sec - t0.tv_sec) * 1e3) +
                      ((t1.tv_nsec - t0.tv_nsec) / 1e6);
    printf("  Total: %.1f ms, Per run: %.2f ms\n",
           total_ms, total_ms / N);
    printf("  (Includes 20 sample forward passes per run)\n");
    printf("  Per-sample: %.3f ms\n", total_ms / N / ZCE_NSAMPLES_IRIS);
}

/* ── Summary ────────────────────────────────────────────── */

void print_summary(TestResult *results, int n) {
    printf("\n%s\n", "══════════════════════════════════════════════════");
    printf("FINAL SUMMARY\n");
    printf("%s\n\n", "══════════════════════════════════════════════════");

    int all_pass = 1;
    for (int i = 0; i < n; i++) {
        TestResult *r = &results[i];
        int pass = (!r->error && r->n_match == r->n_samples);
        all_pass &= pass;
        printf("  %-8s  C==numpy: %2d/%2d  C acc: %2d/%2d  %.2fms  %s\n",
               r->name,
               r->n_match, r->n_samples,
               r->n_c_correct, r->n_samples,
               r->elapsed_ms,
               pass ? "PASS" : (r->error ? "ERROR" : "FAIL"));
    }

    printf("\n  Overall: %s\n", all_pass ? "ALL TESTS PASS ✓" : "SOME TESTS FAILED ✗");

    if (all_pass) {
        printf("\n  What this means:\n");
        printf("  - Python encoder → C decoder round-trip is exact\n");
        printf("  - Weights, DEFINE_OP, MAT_VEC, VEC_ADD, LEAKY_RELU,\n");
        printf("    SOFTMAX, ARGMAX all execute correctly through frozen decoder\n");
        printf("  - The grammar section IS the model\n");
        printf("  - No decoder update needed for any of these networks\n");
    }
}

/* ── Main ───────────────────────────────────────────────── */

int main(void) {
    printf("ZCE v2 Network Decode Tests\n");
    printf("============================\n");
    printf("Decoder: zce_decoder_v2.h (frozen, no ML knowledge)\n");
    printf("Executor: zce_ml_exec.h (ML ops via exec_ext hook)\n");
    printf("Encoder: Python zce_ml_encoder.py\n");
    printf("Networks: Iris, Moons, 4-class Blobs\n");

    TestResult results[3];

    results[0] = run_network_test("iris",
        ZCE_STREAM_IRIS,  ZCE_STREAM_IRIS_LEN,
        ZCE_NPRED_IRIS,   ZCE_TRUE_IRIS,   ZCE_NSAMPLES_IRIS);

    results[1] = run_network_test("moons",
        ZCE_STREAM_MOONS, ZCE_STREAM_MOONS_LEN,
        ZCE_NPRED_MOONS,  ZCE_TRUE_MOONS,  ZCE_NSAMPLES_MOONS);

    results[2] = run_network_test("blobs",
        ZCE_STREAM_BLOBS, ZCE_STREAM_BLOBS_LEN,
        ZCE_NPRED_BLOBS,  ZCE_TRUE_BLOBS,  ZCE_NSAMPLES_BLOBS);

    run_mismatch_test();
    run_timing_benchmark();
    print_summary(results, 3);

    return 0;
}
