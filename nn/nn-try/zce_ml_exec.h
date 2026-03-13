/*
 * zce_ml_exec.h — ML extended executor for zce_decoder_v2.h
 * ==========================================================
 * Provides exec_ext for neural network forward passes.
 *
 * Extended op codes (action_param values):
 *
 *   Integer / control
 *   3   SUB      slots[dst] = slots[a] - slots[b]
 *   4   MUL      slots[dst] = slots[a] * slots[b]
 *   5   DIV      slots[dst] = slots[a] / slots[b]
 *
 *   Float scalar (slots hold float bits reinterpreted)
 *   10  FSET     fslots[dst] = raw32 value (arg is immediate bits)
 *   11  FADD     fslots[dst] = fslots[a] + fslots[b]
 *   12  FSUB     fslots[dst] = fslots[a] - fslots[b]
 *   13  FMUL     fslots[dst] = fslots[a] * fslots[b]
 *   14  FDIV     fslots[dst] = fslots[a] / fslots[b]
 *   15  FEXP     fslots[dst] = expf(fslots[a])
 *   16  FTANH    fslots[dst] = tanhf(fslots[a])
 *   17  FMAX     fslots[dst] = fmaxf(fslots[a], fslots[b])
 *   18  FMIN     fslots[dst] = fminf(fslots[a], fslots[b])
 *   19  FNEG     fslots[dst] = -fslots[a]
 *   20  FABS     fslots[dst] = fabsf(fslots[a])
 *   21  FCMP_GT  slots[dst]  = (fslots[a] > fslots[b]) ? 1 : 0
 *   22  FPRINT   printf fslots[a]
 *
 *   Float arrays (stored in a side array-of-arrays)
 *   30  FARR_NEW  arrays[slots[dst]] = new float[slots[size]]
 *   31  FARR_SET  arrays[slots[arr]][slots[idx]] = fslots[val]
 *   32  FARR_GET  fslots[dst] = arrays[slots[arr]][slots[idx]]
 *
 *   ML vector ops (operate on float arrays)
 *   40  MAT_VEC   out[i] = sum(W[i*cols+j] * x[j])
 *   41  VEC_ADD   out[i] = a[i] + b[i]
 *   42  SOFTMAX   out[i] = exp(x[i]) / sum(exp(x))
 *   43  ARGMAX    slots[dst] = argmax(arr[:n])
 *   44  LEAKY_RELU  arr[i] = max(0,arr[i]) + 0.01*min(0,arr[i])
 *   45  VEC_COPY  dst_arr[i] = src_arr[i]
 *
 * Float slot layout:
 *   The decoder has int64_t slots[4096].
 *   We interpret float slots by storing float bits as int64_t.
 *   fget(d, s) = *(float*)&d->slots[s]
 *   fset(d, s, f) = d->slots[s] = *(int64_t*)(void*)&f_bits
 *
 * Array layout:
 *   Static pool of float arrays. slots[arr_id] holds the array index.
 *   Up to 64 arrays, each up to 4096 floats.
 */

#ifndef ZCE_ML_EXEC_H
#define ZCE_ML_EXEC_H

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* ── Float slot accessors ────────────────────────────────── */

static inline float zce_fget(ZCEDecoder *d, int64_t s) {
    if (s < 0 || s >= ZCE_MAX_SLOTS) return 0.0f;
    uint32_t bits = (uint32_t)(d->slots[s] & 0xFFFFFFFFu);
    float f;
    memcpy(&f, &bits, 4);
    return f;
}

static inline void zce_fset(ZCEDecoder *d, int64_t s, float f) {
    if (s < 0 || s >= ZCE_MAX_SLOTS) return;
    uint32_t bits;
    memcpy(&bits, &f, 4);
    d->slots[s] = (int64_t)bits;
}

/* ── Float array pool ────────────────────────────────────── */

#define ZCE_MAX_ARRAYS   64
#define ZCE_MAX_ARR_LEN  16384

typedef struct {
    float  data[ZCE_MAX_ARR_LEN];
    int    len;
    int    used;
} ZCEArray;

/* Global array pool — reset between models if needed */
static ZCEArray zce_arrays[ZCE_MAX_ARRAYS];
static int      zce_n_arrays = 0;

static void zce_arrays_reset(void) {
    memset(zce_arrays, 0, sizeof zce_arrays);
    zce_n_arrays = 0;
}

static int zce_arr_new(int size) {
    if (zce_n_arrays >= ZCE_MAX_ARRAYS || size > ZCE_MAX_ARR_LEN || size < 0)
        return -1;
    int id = zce_n_arrays++;
    memset(zce_arrays[id].data, 0, size * sizeof(float));
    zce_arrays[id].len  = size;
    zce_arrays[id].used = 1;
    return id;
}

static float zce_arr_get(int arr_id, int idx) {
    if (arr_id < 0 || arr_id >= zce_n_arrays) return 0.0f;
    ZCEArray *a = &zce_arrays[arr_id];
    if (idx < 0 || idx >= a->len) return 0.0f;
    return a->data[idx];
}

static void zce_arr_set(int arr_id, int idx, float val) {
    if (arr_id < 0 || arr_id >= zce_n_arrays) return;
    ZCEArray *a = &zce_arrays[arr_id];
    if (idx < 0 || idx >= a->len) return;
    a->data[idx] = val;
}

/* ── Extended executor ───────────────────────────────────── */

static void zce_ml_exec(ZCEDecoder *d, int param, int64_t *args) {
    switch (param) {

    /* ── Integer ops ─────────────────────────────────── */
    case 3: /* SUB dst a b */
        d->slots[args[0]] = d->slots[args[1]] - d->slots[args[2]]; break;
    case 4: /* MUL dst a b */
        d->slots[args[0]] = d->slots[args[1]] * d->slots[args[2]]; break;
    case 5: /* DIV dst a b */
        if (d->slots[args[2]])
            d->slots[args[0]] = d->slots[args[1]] / d->slots[args[2]];
        break;

    /* ── Float scalar ops ────────────────────────────── */
    case 10: /* FSET dst raw32_val — args[1] is raw bits */
        d->slots[args[0]] = args[1] & 0xFFFFFFFFu;
        break;
    case 11: /* FADD dst a b */
        zce_fset(d, args[0], zce_fget(d, args[1]) + zce_fget(d, args[2])); break;
    case 12: /* FSUB dst a b */
        zce_fset(d, args[0], zce_fget(d, args[1]) - zce_fget(d, args[2])); break;
    case 13: /* FMUL dst a b */
        zce_fset(d, args[0], zce_fget(d, args[1]) * zce_fget(d, args[2])); break;
    case 14: /* FDIV dst a b */
        { float b = zce_fget(d, args[2]);
          zce_fset(d, args[0], b != 0.0f ? zce_fget(d, args[1]) / b : 0.0f);
          break; }
    case 15: /* FEXP dst a */
        { float v = zce_fget(d, args[1]);
          if (v >  88.0f) v =  88.0f;
          if (v < -88.0f) v = -88.0f;
          zce_fset(d, args[0], expf(v)); break; }
    case 16: /* FTANH dst a */
        zce_fset(d, args[0], tanhf(zce_fget(d, args[1]))); break;
    case 17: /* FMAX dst a b */
        zce_fset(d, args[0], fmaxf(zce_fget(d, args[1]), zce_fget(d, args[2]))); break;
    case 18: /* FMIN dst a b */
        zce_fset(d, args[0], fminf(zce_fget(d, args[1]), zce_fget(d, args[2]))); break;
    case 19: /* FNEG dst a */
        zce_fset(d, args[0], -zce_fget(d, args[1])); break;
    case 20: /* FABS dst a */
        zce_fset(d, args[0], fabsf(zce_fget(d, args[1]))); break;
    case 21: /* FCMP_GT dst a b → int result */
        d->slots[args[0]] = (zce_fget(d, args[1]) > zce_fget(d, args[2])) ? 1 : 0;
        break;
    case 22: /* FPRINT a */
        printf("  fslot[%lld] = %f\n", (long long)args[0], zce_fget(d, args[0]));
        break;

    /* ── Float array ops ─────────────────────────────── */
    case 30: /* FARR_NEW dst_slot size_slot */
        { int size = (int)d->slots[args[1]];
          int id   = zce_arr_new(size);
          d->slots[args[0]] = id;
          break; }
    case 31: /* FARR_SET arr_slot idx_slot fval_slot */
        { int arr = (int)d->slots[args[0]];
          int idx = (int)d->slots[args[1]];
          float val = zce_fget(d, args[2]);
          zce_arr_set(arr, idx, val);
          break; }
    case 32: /* FARR_GET dst_fslot arr_slot idx_slot */
        { int arr = (int)d->slots[args[1]];
          int idx = (int)d->slots[args[2]];
          zce_fset(d, args[0], zce_arr_get(arr, idx));
          break; }

    /* ── ML vector ops ───────────────────────────────── */
    case 40: /* MAT_VEC out_arr W_arr x_arr rows_slot cols_slot */
        { int out_id = (int)d->slots[args[0]];
          int W_id   = (int)d->slots[args[1]];
          int x_id   = (int)d->slots[args[2]];
          int rows   = (int)d->slots[args[3]];
          int cols   = (int)d->slots[args[4]];
          for (int i = 0; i < rows; i++) {
              float s = 0.0f;
              for (int j = 0; j < cols; j++)
                  s += zce_arr_get(W_id, i*cols+j) * zce_arr_get(x_id, j);
              zce_arr_set(out_id, i, s);
          }
          break; }

    case 41: /* VEC_ADD out_arr a_arr b_arr n_slot */
        { int out_id = (int)d->slots[args[0]];
          int a_id   = (int)d->slots[args[1]];
          int b_id   = (int)d->slots[args[2]];
          int n      = (int)d->slots[args[3]];
          for (int i = 0; i < n; i++)
              zce_arr_set(out_id, i,
                  zce_arr_get(a_id, i) + zce_arr_get(b_id, i));
          break; }

    case 42: /* SOFTMAX arr n_slot (in-place) */
        { int arr_id = (int)d->slots[args[0]];
          int n      = (int)d->slots[args[1]];
          float mx   = -1e30f;
          for (int i = 0; i < n; i++) {
              float v = zce_arr_get(arr_id, i);
              if (v > mx) mx = v;
          }
          float sum = 0.0f;
          for (int i = 0; i < n; i++) {
              float e = expf(fminf(zce_arr_get(arr_id, i) - mx, 88.0f));
              zce_arr_set(arr_id, i, e);
              sum += e;
          }
          if (sum > 0.0f)
              for (int i = 0; i < n; i++)
                  zce_arr_set(arr_id, i, zce_arr_get(arr_id, i) / sum);
          break; }

    case 43: /* ARGMAX dst_slot arr_slot n_slot */
        { int arr_id = (int)d->slots[args[1]];
          int n      = (int)d->slots[args[2]];
          int best   = 0;
          float bval = zce_arr_get(arr_id, 0);
          for (int i = 1; i < n; i++) {
              float v = zce_arr_get(arr_id, i);
              if (v > bval) { bval = v; best = i; }
          }
          d->slots[args[0]] = best;
          break; }

    case 44: /* LEAKY_RELU arr n_slot (in-place, alpha=0.01) */
        { int arr_id = (int)d->slots[args[0]];
          int n      = (int)d->slots[args[1]];
          for (int i = 0; i < n; i++) {
              float v = zce_arr_get(arr_id, i);
              zce_arr_set(arr_id, i, v > 0.0f ? v : 0.01f * v);
          }
          break; }

    case 45: /* VEC_COPY dst_arr src_arr n_slot */
        { int dst = (int)d->slots[args[0]];
          int src = (int)d->slots[args[1]];
          int n   = (int)d->slots[args[2]];
          for (int i = 0; i < n; i++)
              zce_arr_set(dst, i, zce_arr_get(src, i));
          break; }

    default:
        /* Unknown op — silently skip (forward compatible) */
        break;
    }
}

#endif /* ZCE_ML_EXEC_H */
/* ── Additional ops for surgery testing ─────────────────────
   These have identical interfaces to their counterparts,
   enabling in-stream activation swaps with correct semantics:

   46  ARRAY_TANH     arr[i] = tanh(arr[i])    (same interface as LEAKY_RELU)
   47  ARRAY_RELU     arr[i] = max(0, arr[i])   (hard relu)
   48  ARRAY_SIGMOID  arr[i] = 1/(1+exp(-arr[i]))
*/
#ifndef ZCE_EXTRA_OPS_DEFINED
#define ZCE_EXTRA_OPS_DEFINED
static void zce_ml_exec_extra(ZCEDecoder *d, int param, int64_t *args) {
    /* Call base ops first */
    if (param < 46) { zce_ml_exec(d, param, args); return; }
    switch (param) {
    case 46: { /* ARRAY_TANH */
        int arr=(int)d->slots[args[0]], n=(int)d->slots[args[1]];
        for (int i=0;i<n;i++) zce_arr_set(arr,i,tanhf(zce_arr_get(arr,i)));
        break; }
    case 47: { /* ARRAY_RELU */
        int arr=(int)d->slots[args[0]], n=(int)d->slots[args[1]];
        for (int i=0;i<n;i++) { float v=zce_arr_get(arr,i); zce_arr_set(arr,i,fmaxf(v,0.f)); }
        break; }
    case 48: { /* ARRAY_SIGMOID */
        int arr=(int)d->slots[args[0]], n=(int)d->slots[args[1]];
        for (int i=0;i<n;i++) { float v=zce_arr_get(arr,i); zce_arr_set(arr,i,1.f/(1.f+expf(-v))); }
        break; }
    default: break;
    }
}
#endif /* ZCE_EXTRA_OPS_DEFINED */
