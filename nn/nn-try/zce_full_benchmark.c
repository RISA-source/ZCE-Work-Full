/*
 * zce_full_benchmark.c — ZCE v2 Complete Benchmark
 * Scale, Token Surgery, Weight Transfer, Timing
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "zce_decoder.h"
#include "zce_ml_exec.h"
#include "zce_full_benchmark_streams.h"

static double now_ms(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec*1e3 + t.tv_nsec/1e6;
}

/* Wrong executor: uses tanh instead of leaky_relu */
static void exec_tanh_wrong(ZCEDecoder *d, int param, int64_t *args) {
    if (param == 44) {  /* LEAKY_RELU → tanh */
        int arr=(int)d->slots[args[0]], n=(int)d->slots[args[1]];
        for (int i=0;i<n;i++) zce_arr_set(arr,i,tanhf(zce_arr_get(arr,i)));
    } else zce_ml_exec_extra(d, param, args);
}

static int run_stream(const uint8_t *s, int len, int n, void (*exec)(ZCEDecoder*,int,int64_t*),
                      int *out_preds) {
    zce_arrays_reset();
    ZCEDecoder d; zce_init(&d, s, len); d.exec_ext = exec;
    int ok = zce_run(&d);
    if (ok != 0) { fprintf(stderr,"  ERROR: %s\n",d.errmsg); return -1; }
    if (out_preds) for (int i=0;i<n;i++) out_preds[i]=(int)zce_slot(&d,50+i);
    return d.steps;
}

static int count_correct(int *preds, const int *true_lbl, int n) {
    int c=0; for (int i=0;i<n;i++) c+=(preds[i]==true_lbl[i]); return c;
}
static int count_match(int *a, const int *b, int n) {
    int c=0; for (int i=0;i<n;i++) c+=(a[i]==b[i]); return c;
}

int main(void) {
    printf("ZCE v2 Complete Benchmark\n");
    printf("==========================\n");
    printf("Frozen decoder: zce_decoder_v2.h  |  Executor: zce_ml_exec.h\n\n");

    /* ── SCALE TESTS ── */
    printf("══ SCALE TESTS ═══════════════════════════════════════════════\n\n");
    printf("  %-14s %-14s %7s %8s %7s %8s  %s\n",
           "Test","Arch","Params","Stream","C==NP","Acc","Status");
    printf("  %s\n","──────────────────────────────────────────────────────────────");

    struct { const char *name,*arch; const uint8_t *s; int len,n,np; const int *npred,*true_l; } scale[] = {
        {"moons_8","2→8→2",STREAM_MOONS_8,STREAM_MOONS_8_LEN,TRUE_MOONS_8_N,42,
            NPRED_MOONS_8,TRUE_MOONS_8},
        {"digits_32","64→32→10",STREAM_DIGITS_32,STREAM_DIGITS_32_LEN,TRUE_DIGITS_32_N,2410,
            NPRED_DIGITS_32,TRUE_DIGITS_32},
        {"digits_64","64→64→10",STREAM_DIGITS_64,STREAM_DIGITS_64_LEN,TRUE_DIGITS_64_N,4810,
            NPRED_DIGITS_64,TRUE_DIGITS_64},
        {"digits_128","64→128→10",STREAM_DIGITS_128,STREAM_DIGITS_128_LEN,TRUE_DIGITS_128_N,9610,
            NPRED_DIGITS_128,TRUE_DIGITS_128},
    };
    int all_pass=1;
    int preds[20];
    for (int i=0;i<4;i++) {
        run_stream(scale[i].s,scale[i].len,scale[i].n,zce_ml_exec_extra,preds);
        int match=count_match(preds,scale[i].npred,scale[i].n);
        int correct=count_correct(preds,scale[i].true_l,scale[i].n);
        int pass=(match==scale[i].n);
        all_pass&=pass;
        printf("  %-14s %-14s %7d %8d %5d/%-2d %6.1f%%  %s\n",
               scale[i].name,scale[i].arch,scale[i].np,scale[i].len,
               match,scale[i].n, 100.0*correct/scale[i].n,
               pass?"PASS":"FAIL");
    }

    /* ── TOKEN SURGERY ── */
    printf("\n══ TOKEN SURGERY (activation swap) ═══════════════════════════\n\n");

    int n=TRUE_MOONS_8_N;
    const int *true_m=TRUE_MOONS_8;

    /* Original stream, correct executor */
    int preds_lr[20], preds_tanh_exec[20], preds_surgery[20];
    run_stream(STREAM_MOONS_8,STREAM_MOONS_8_LEN,n,zce_ml_exec_extra,preds_lr);
    /* Original stream, WRONG executor */
    run_stream(STREAM_MOONS_8,STREAM_MOONS_8_LEN,n,exec_tanh_wrong,preds_tanh_exec);
    /* Surgery stream (1 bit flipped: op44→op46), correct executor */
    run_stream(STREAM_MOONS_TANH,STREAM_MOONS_TANH_LEN,n,zce_ml_exec_extra,preds_surgery);

    int lr_correct     = count_correct(preds_lr,true_m,n);
    int wrong_correct  = count_correct(preds_tanh_exec,true_m,n);
    int surgery_correct= count_correct(preds_surgery,true_m,n);
    int surgery_vs_np  = count_match(preds_surgery,NPRED_MOONS_TANH,n);
    int surgery_vs_exec= count_match(preds_surgery,preds_tanh_exec,n);

    printf("  Original stream  + correct exec (leaky_relu): %d/%d (%.1f%%)\n",
           lr_correct, n, 100.0*lr_correct/n);
    printf("  Original stream  + wrong   exec (tanh):       %d/%d (%.1f%%)\n",
           wrong_correct, n, 100.0*wrong_correct/n);
    printf("  Acc drop (executor swap only):                 %+d points\n",
           lr_correct-wrong_correct);
    printf("\n  Surgery: 1 bit flipped in grammar (op44→op46, LEAKY_RELU→ARRAY_TANH)\n");
    printf("  Surgered stream + correct exec (leaky_relu):  %d/%d (%.1f%%)\n",
           surgery_correct, n, 100.0*surgery_correct/n);
    printf("  Surgered stream matches tanh numpy preds:     %d/%d\n",surgery_vs_np,n);
    printf("  Surgered stream == wrong executor on original: %d/%d\n",surgery_vs_exec,n);
    int surgery_pass = (surgery_vs_np==n && surgery_vs_exec==n);
    all_pass &= surgery_pass;
    printf("  %s\n", surgery_pass ?
        "✓ 1-bit surgery = full executor swap: grammar encodes computation" :
        "✗ Surgery/executor equivalence failed");

    /* ── WEIGHT SURGERY / TRANSFER ── */
    printf("\n══ WEIGHT SURGERY / TRANSFER ══════════════════════════════════\n\n");

    int preds_a[20], preds_transfer[20];
    run_stream(STREAM_MOONS_8,STREAM_MOONS_8_LEN,n,zce_ml_exec_extra,preds_a);
    run_stream(STREAM_MOONS_TRANSFER,STREAM_MOONS_TRANSFER_LEN,n,zce_ml_exec_extra,preds_transfer);

    int a_correct  = count_correct(preds_a,true_m,n);
    int t_correct  = count_correct(preds_transfer,true_m,n);
    int t_match_np = count_match(preds_transfer,NPRED_MOONS_TRANSFER,n);
    int transfer_pass = (t_match_np==n);
    all_pass &= transfer_pass;
    printf("  Model A (original backbone+head):              %d/%d (%.1f%%)\n",
           a_correct,n,100.0*a_correct/n);
    printf("  Transplanted (backbone A + output layer B):    %d/%d (%.1f%%)\n",
           t_correct,n,100.0*t_correct/n);
    printf("  C transplant matches numpy reference:          %d/%d\n",t_match_np,n);
    printf("  Acc delta: %+d points\n", t_correct-a_correct);
    printf("  %s\n", transfer_pass ?
        "✓ Weight surgery verified: C decoder matches numpy transplant exactly" :
        "✗ Transplant mismatch");

    /* ── TIMING ── */
    printf("\n══ TIMING BENCHMARK (100 runs each) ══════════════════════════\n\n");
    printf("  %-14s %-12s %8s %9s %9s %10s\n",
           "Network","Arch","Params","StreamB","ms/run","μs/sample");
    printf("  %s\n","────────────────────────────────────────────────────────────");

    struct { const char *name,*arch; const uint8_t *s; int len,n,np; } tc[] = {
        {"moons_8","2→8→2",STREAM_MOONS_8,STREAM_MOONS_8_LEN,TRUE_MOONS_8_N,42},
        {"digits_32","64→32→10",STREAM_DIGITS_32,STREAM_DIGITS_32_LEN,TRUE_DIGITS_32_N,2410},
        {"digits_64","64→64→10",STREAM_DIGITS_64,STREAM_DIGITS_64_LEN,TRUE_DIGITS_64_N,4810},
        {"digits_128","64→128→10",STREAM_DIGITS_128,STREAM_DIGITS_128_LEN,TRUE_DIGITS_128_N,9610},
    };
    int REPS=100;
    for (int i=0;i<4;i++) {
        /* warmup */
        for (int r=0;r<3;r++) run_stream(tc[i].s,tc[i].len,tc[i].n,zce_ml_exec_extra,NULL);
        double t0=now_ms();
        for (int r=0;r<REPS;r++) run_stream(tc[i].s,tc[i].len,tc[i].n,zce_ml_exec_extra,NULL);
        double ms=(now_ms()-t0)/REPS;
        printf("  %-14s %-12s %8d %9d %9.3f %10.2f\n",
               tc[i].name,tc[i].arch,tc[i].np,tc[i].len,ms,ms*1000.0/tc[i].n);
    }

    /* ── SUMMARY ── */
    printf("\n══════════════════════════════════════════════════════════════\n");
    printf("FINAL RESULT: %s\n\n", all_pass ? "ALL TESTS PASS ✓" : "SOME TESTS FAILED");
    if (all_pass) {
        printf("  What is demonstrated:\n");
        printf("  1. SCALE: C decoder correctly runs 2→8→2 through 64→128→10\n");
        printf("  2. TOKEN SURGERY: 1 bit flip in grammar = full activation swap\n");
        printf("     (grammar section carries computational meaning, not just metadata)\n");
        printf("  3. WEIGHT SURGERY: transplant output layer → exact numpy match\n");
        printf("  4. FORMAT: any stream runs on frozen decoder, no recompilation\n");
    }
    return all_pass ? 0 : 1;
}
