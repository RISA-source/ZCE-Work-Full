import math, struct, sys
from copy import deepcopy

def eg_enc(v):
    assert v >= 0
    n = v + 1; k = int(math.log2(n))
    return '0'*k + format(n, f'0{k+1}b')

def eg_dec(bits, pos):
    k = 0
    while pos < len(bits) and bits[pos] == '0': k += 1; pos += 1
    if pos + k >= len(bits): raise ValueError(f"Elias decode off end pos={pos}")
    n = int(bits[pos:pos+k+1], 2)
    return n-1, pos+k+1

def raw16(n):  return format(n & 0xFFFF, '016b')
def r16(b):    return int(b, 2)
def tok(n, d): return '0'*n + '1'*d + '0'
def ptr(v):    return eg_enc(v)
def f32_enc(f): return format(struct.unpack('I', struct.pack('f', float(f)))[0], '032b')
def f32_dec(b): return struct.unpack('f', struct.pack('I', int(b, 2)))[0]

BASE_PRIMITIVES = {
    0:  ('FADD',       lambda s,a,b,c: s.__setitem__(c, s[a] + s[b])),
    1:  ('FSUB',       lambda s,a,b,c: s.__setitem__(c, s[a] - s[b])),
    2:  ('FMUL',       lambda s,a,b,c: s.__setitem__(c, s[a] * s[b])),
    3:  ('FDIV',       lambda s,a,b,c: s.__setitem__(c, s[a] / s[b] if s[b] != 0 else 0.0)),
    4:  ('FEXP',       lambda s,a,b,c: s.__setitem__(c, math.exp(min(float(s[a]), 88.0)))),
    5:  ('FTANH',      lambda s,a,b,c: s.__setitem__(c, math.tanh(float(s[a])))),
    6:  ('FABS',       lambda s,a,b,c: s.__setitem__(c, abs(float(s[a])))),
    7:  ('FNEG',       lambda s,a,b,c: s.__setitem__(c, -float(s[a]))),
    8:  ('FMAX',       lambda s,a,b,c: s.__setitem__(c, max(s[a], s[b]))),
    9:  ('FMIN',       lambda s,a,b,c: s.__setitem__(c, min(s[a], s[b]))),
    10: ('FCONST_0',   lambda s,a,b,c: s.__setitem__(c, 0.0)),
    11: ('FCONST_1',   lambda s,a,b,c: s.__setitem__(c, 1.0)),
    12: ('FCONST_NEG1',lambda s,a,b,c: s.__setitem__(c, -1.0)),
}
BASE_PRIM_NAMES = {v[0]: k for k, v in BASE_PRIMITIVES.items()}

INSTR = {1:'ADD',2:'SUB',3:'MUL',4:'DIV',5:'MOD',6:'LOAD',7:'PRINT',
         8:'CMP_LT',9:'CMP_GT',10:'CMP_EQ',11:'CMP_NEQ',12:'CMP_LTE',13:'CMP_GTE'}
INSTR_R = {v:k for k,v in INSTR.items()}
INSTR_ARITY = {'ADD':3,'SUB':3,'MUL':3,'DIV':3,'MOD':3,'LOAD':2,'PRINT':1,
               'CMP_LT':3,'CMP_GT':3,'CMP_EQ':3,'CMP_NEQ':3,'CMP_LTE':3,'CMP_GTE':3}

FLOAT_INSTR = {1:'FADD_S',2:'FSUB_S',3:'FMUL_S',4:'FDIV_S',5:'FLOAD_S',6:'FPRINT_S',
               7:'FCMP_LT',8:'FCMP_GT',9:'FCMP_EQ',10:'FCMP_NEQ',11:'FCMP_LTE',12:'FCMP_GTE',
               13:'INT_TO_FLOAT',14:'FLOAT_TO_INT',15:'FEXP_S',16:'FTANH_S',17:'FSQRT_S',18:'FABS_S',
               19:'MAT_VEC',20:'VEC_ADD',21:'APPLY_OP',22:'SOFTMAX_VEC',23:'ARGMAX',
               24:'FGET',25:'FSET',26:'FARR_NEW',27:'FARR_LEN',28:'FPRINT_ARR'}
FLOAT_INSTR_R = {v:k for k,v in FLOAT_INSTR.items()}
FLOAT_INSTR_ARITY = {'FADD_S':3,'FSUB_S':3,'FMUL_S':3,'FDIV_S':3,'FLOAD_S':2,'FPRINT_S':1,
                     'FCMP_LT':3,'FCMP_GT':3,'FCMP_EQ':3,'FCMP_NEQ':3,'FCMP_LTE':3,'FCMP_GTE':3,
                     'INT_TO_FLOAT':2,'FLOAT_TO_INT':2,'FEXP_S':2,'FTANH_S':2,'FSQRT_S':2,'FABS_S':2,
                     'MAT_VEC':5,'VEC_ADD':4,'APPLY_OP':4,'SOFTMAX_VEC':3,'ARGMAX':3,
                     'FGET':3,'FSET':3,'FARR_NEW':2,'FARR_LEN':2,'FPRINT_ARR':2}

D_TOP=1; D_FUNC=2; D_BLOCK=3

def encode(instructions, data_values, float_slots=None):
    if float_slots is None: float_slots = set()
    g = [tok(7,1), tok(5,1)]
    for instr in instructions:
        op=instr['op']; args=instr.get('args',[]); d=instr.get('depth',D_TOP)
        if op=='JMP': g.append(tok(8,d)); g.append(ptr(instr['jump_to']))
        elif op=='JIF': g.append(tok(6,d)); g.append(ptr(args[0])); g.append(ptr(instr['jump_to']))
        elif op=='FUNC':
            g.append(tok(9,d)); g.append(ptr(args[0])); g.append(ptr(args[1]))
            for ps in args[2:]: g.append(ptr(ps))
        elif op=='CALL':
            g.append(tok(10,d)); g.append(ptr(args[0])); g.append(ptr(args[1])); g.append(ptr(args[2]))
            for a in args[3:]: g.append(ptr(a))
        elif op=='RET': g.append(tok(11,d)); g.append(ptr(args[0]))
        elif op=='DEFINE_OP':
            g.append(tok(15,d)); g.append(ptr(instr['op_id'])); g.append(ptr(instr['n_inputs']))
            g.append(ptr(instr['n_outputs'])); g.append(ptr(len(instr['steps'])))
            for (pcode,a,b,c) in instr['steps']:
                g.append(ptr(pcode)); g.append(ptr(a)); g.append(ptr(b)); g.append(ptr(c))
        elif op=='CALL_OP':
            g.append(tok(16,d))
            for a in args: g.append(ptr(a))
        elif op in FLOAT_INSTR_R:
            g.append(tok(14,d)); g.append(tok(FLOAT_INSTR_R[op],d))
            for a in args: g.append(ptr(a))
        else:
            g.append(tok(2,d)); g.append(tok(INSTR_R[op],d))
            for a in args: g.append(ptr(a))
    g += [tok(5,1), tok(7,1)]
    grammar = ''.join(g)
    data_parts = []
    for i,v in enumerate(data_values):
        if i in float_slots: data_parts.append(f32_enc(v))
        else: data_parts.append(eg_enc(int(v) if not isinstance(v,float) else 0))
    data_enc = ''.join(data_parts)
    header = raw16(len(grammar)) + raw16(len(data_values))
    return header + grammar + data_enc, float_slots

def decode(bs, float_slots=None):
    if float_slots is None: float_slots = set()
    gl=r16(bs[:16]); dc=r16(bs[16:32])
    gram=bs[32:32+gl]; draw=bs[32+gl:]
    pos2,data=0,[]
    for i in range(dc):
        if i in float_slots: data.append(f32_dec(draw[pos2:pos2+32])); pos2+=32
        else: v,pos2=eg_dec(draw,pos2); data.append(v)
    user_ops={}; ops=[]; pos=0
    def rp():
        nonlocal pos; v,pos=eg_dec(gram,pos); return v
    def rt():
        nonlocal pos
        n=0
        while pos<len(gram) and gram[pos]=='0': n+=1; pos+=1
        m=0
        while pos<len(gram) and gram[pos]=='1': m+=1; pos+=1
        if pos<len(gram) and gram[pos]=='0': pos+=1
        return n,m
    while pos<len(gram):
        n,depth=rt()
        if n==0: continue
        if n in (7,5): continue
        if n==8: tgt=rp(); ops.append({'op':'JMP','args':[],'jump_to':tgt,'depth':depth})
        elif n==6: cond=rp(); tgt=rp(); ops.append({'op':'JIF','args':[cond],'jump_to':tgt,'depth':depth})
        elif n==9:
            fid=rp(); npr=rp(); ps=[rp() for _ in range(npr)]
            ops.append({'op':'FUNC','args':[fid,npr]+ps,'depth':depth})
        elif n==10:
            fid=rp(); na=rp(); res=rp(); ca=[rp() for _ in range(na)]
            ops.append({'op':'CALL','args':[fid,na,res]+ca,'depth':depth})
        elif n==11: rv=rp(); ops.append({'op':'RET','args':[rv],'depth':depth})
        elif n==15:
            op_id=rp(); n_in=rp(); n_out=rp(); n_steps=rp()
            steps=[]
            for _ in range(n_steps):
                pcode=rp(); a=rp(); b=rp(); c=rp(); steps.append((pcode,a,b,c))
            user_ops[op_id]={'n_inputs':n_in,'n_outputs':n_out,'steps':steps}
            ops.append({'op':'DEFINE_OP','op_id':op_id,'user_ops':user_ops,'depth':depth})
        elif n==16:
            op_id=rp(); x_slot=rp(); out_slot=rp(); n_slot=rp()
            ops.append({'op':'CALL_OP','args':[op_id,x_slot,out_slot,n_slot],'user_ops':user_ops,'depth':depth})
        elif n==14:
            ic,_=rt(); iop=FLOAT_INSTR.get(ic,f'UNK_F{ic}')
            arity=FLOAT_INSTR_ARITY.get(iop,0); iargs=[rp() for _ in range(arity)]
            ops.append({'op':iop,'args':iargs,'depth':depth})
        elif n==2:
            ic,_=rt(); iop=INSTR.get(ic,f'UNK{ic}')
            arity=INSTR_ARITY.get(iop,0); iargs=[rp() for _ in range(arity)]
            ops.append({'op':iop,'args':iargs,'depth':depth})
    return ops,data

class GenericVM:
    def __init__(self, max_steps=50_000_000):
        self.output=[]; self.max_steps=max_steps
        self.func_local_slots={}; self.ops_executed={}

    def execute_user_op(self, op_def, input_val):
        n_in=op_def['n_inputs']; n_out=op_def['n_outputs']; steps=op_def['steps']
        max_slot=max((c for _,_,_,c in steps),default=0)
        n_slots=max(n_in+n_out,max_slot+1); slots=[0.0]*n_slots
        slots[0]=float(input_val)
        for (pcode,a,b,c) in steps:
            if pcode in BASE_PRIMITIVES: BASE_PRIMITIVES[pcode][1](slots,a,b,c)
            else: raise ValueError(f"INVALID: primitive {pcode} not in BASE_PRIMITIVES")
        return slots[n_in] if n_in<len(slots) else 0.0

    def run(self, bitstream, float_slots=None):
        if float_slots is None: float_slots=set()
        ops,data=decode(bitstream,float_slots); data=list(data)
        farrays=[]; user_ops_runtime={}
        ftable={}
        for idx,op in enumerate(ops):
            if op['op']=='FUNC':
                fid=op['args'][0]; npr=op['args'][1]; pslots=op['args'][2:2+npr]
                lslots=self.func_local_slots.get(fid,set(pslots))
                ftable[fid]={'entry':idx,'nparams':npr,'param_slots':pslots,'local_slots':lslots}
        def ext(s):
            while s>=len(data): data.append(0)
        def safe_fget(fid,idx):
            if fid<len(farrays) and 0<=idx<len(farrays[fid]): return farrays[fid][idx]
            return 0.0
        def safe_fset(fid,idx,val):
            if fid<len(farrays) and 0<=idx<len(farrays[fid]): farrays[fid][idx]=float(val)
        pc=0; steps=0; cstack=[]
        while pc<len(ops):
            if steps>self.max_steps: print('  [VM: step limit]'); break
            steps+=1; op=ops[pc]; name=op['op']; args=op.get('args',[])
            if name=='DEFINE_OP': user_ops_runtime[op['op_id']]=op['user_ops'][op['op_id']]
            elif name=='CALL_OP':
                op_id=int(data[args[0]]); x_slot=args[1]; out_slot=args[2]; n_slot=args[3]
                if op_id not in user_ops_runtime: raise ValueError(f"CALL_OP: op_id {op_id} not defined")
                op_def=user_ops_runtime[op_id]
                x_id=int(data[x_slot]); out_id=int(data[out_slot]); n=int(data[n_slot])
                x=farrays[x_id] if x_id<len(farrays) else []
                out=farrays[out_id] if out_id<len(farrays) else []
                for i in range(min(n,len(x),len(out))): out[i]=self.execute_user_op(op_def,x[i])
                self.ops_executed[op_id]=self.ops_executed.get(op_id,0)+1
            elif name=='FADD_S' and len(args)>=3: ext(args[2]); data[args[2]]=data[args[0]]+data[args[1]]
            elif name=='FSUB_S' and len(args)>=3: ext(args[2]); data[args[2]]=data[args[0]]-data[args[1]]
            elif name=='FMUL_S' and len(args)>=3: ext(args[2]); data[args[2]]=data[args[0]]*data[args[1]]
            elif name=='FDIV_S' and len(args)>=3:
                ext(args[2]); data[args[2]]=data[args[0]]/data[args[1]] if data[args[1]] else 0.0
            elif name=='FLOAD_S' and len(args)>=2: ext(args[1]); data[args[1]]=data[args[0]]
            elif name=='FPRINT_S' and len(args)>=1:
                v=data[args[0]]; self.output.append(v); print(f'  → {v:.6f}')
            elif name=='INT_TO_FLOAT' and len(args)>=2: ext(args[1]); data[args[1]]=float(data[args[0]])
            elif name=='FLOAT_TO_INT' and len(args)>=2: ext(args[1]); data[args[1]]=int(data[args[0]])
            elif name=='FEXP_S' and len(args)>=2:
                ext(args[1])
                try: data[args[1]]=math.exp(min(float(data[args[0]]),88.0))
                except: data[args[1]]=0.0
            elif name=='FTANH_S' and len(args)>=2: ext(args[1]); data[args[1]]=math.tanh(float(data[args[0]]))
            elif name=='FSQRT_S' and len(args)>=2:
                ext(args[1]); v=float(data[args[0]]); data[args[1]]=math.sqrt(v) if v>=0 else 0.0
            elif name=='FABS_S' and len(args)>=2: ext(args[1]); data[args[1]]=abs(float(data[args[0]]))
            elif name in ('FCMP_LT','FCMP_GT','FCMP_EQ','FCMP_NEQ','FCMP_LTE','FCMP_GTE') and len(args)>=3:
                ext(args[2])
                ops_map={'FCMP_LT':lambda a,b:a<b,'FCMP_GT':lambda a,b:a>b,'FCMP_EQ':lambda a,b:a==b,
                         'FCMP_NEQ':lambda a,b:a!=b,'FCMP_LTE':lambda a,b:a<=b,'FCMP_GTE':lambda a,b:a>=b}
                data[args[2]]=1 if ops_map[name](data[args[0]],data[args[1]]) else 0
            elif name in ('ADD','SUB','MUL') and len(args)>=3:
                ext(args[2])
                if name=='ADD': data[args[2]]=(data[args[0]]+data[args[1]])&0xFFFF
                elif name=='SUB': data[args[2]]=(data[args[0]]-data[args[1]])&0xFFFF
                elif name=='MUL': data[args[2]]=(data[args[0]]*data[args[1]])&0xFFFF
            elif name=='DIV' and len(args)>=3:
                ext(args[2]); data[args[2]]=(data[args[0]]//data[args[1]]) if data[args[1]] else 0
            elif name=='LOAD' and len(args)>=2: ext(args[1]); data[args[1]]=data[args[0]]
            elif name=='PRINT' and len(args)>=1:
                v=data[args[0]]; self.output.append(v); print(f'  → {v}')
            elif name in ('CMP_LT','CMP_GT','CMP_EQ','CMP_NEQ','CMP_LTE','CMP_GTE') and len(args)>=3:
                ext(args[2])
                ops_map2={'CMP_LT':lambda a,b:a<b,'CMP_GT':lambda a,b:a>b,'CMP_EQ':lambda a,b:a==b,
                          'CMP_NEQ':lambda a,b:a!=b,'CMP_LTE':lambda a,b:a<=b,'CMP_GTE':lambda a,b:a>=b}
                data[args[2]]=1 if ops_map2[name](data[args[0]],data[args[1]]) else 0
            elif name=='FARR_NEW' and len(args)>=2:
                ext(args[1]); size=int(data[args[0]]); arr_id=len(farrays)
                farrays.append([0.0]*size); data[args[1]]=arr_id
            elif name=='FARR_LEN' and len(args)>=2:
                ext(args[1]); arr_id=int(data[args[0]])
                data[args[1]]=len(farrays[arr_id]) if arr_id<len(farrays) else 0
            elif name=='FGET' and len(args)>=3:
                ext(args[2]); arr_id=int(data[args[0]]); idx=int(data[args[1]])
                data[args[2]]=safe_fget(arr_id,idx)
            elif name=='FSET' and len(args)>=3:
                arr_id=int(data[args[0]]); idx=int(data[args[1]]); val=float(data[args[2]])
                safe_fset(arr_id,idx,val)
            elif name=='FPRINT_ARR' and len(args)>=2:
                arr_id=int(data[args[0]]); n=int(data[args[1]])
                arr=farrays[arr_id] if arr_id<len(farrays) else []
                print(f'  arr[:{n}] = {[round(x,4) for x in arr[:n]]}')
            elif name=='MAT_VEC' and len(args)>=5:
                W_id=int(data[args[0]]); x_id=int(data[args[1]]); out_id=int(data[args[2]])
                rows=int(data[args[3]]); cols=int(data[args[4]])
                W=farrays[W_id] if W_id<len(farrays) else []
                x=farrays[x_id] if x_id<len(farrays) else []
                out=farrays[out_id] if out_id<len(farrays) else []
                for i in range(min(rows,len(out))):
                    s=0.0
                    for j in range(min(cols,len(x))):
                        if i*cols+j<len(W): s+=W[i*cols+j]*x[j]
                    out[i]=s
            elif name=='VEC_ADD' and len(args)>=4:
                a_id=int(data[args[0]]); b_id=int(data[args[1]]); out_id=int(data[args[2]]); n=int(data[args[3]])
                a=farrays[a_id] if a_id<len(farrays) else []
                b=farrays[b_id] if b_id<len(farrays) else []
                out=farrays[out_id] if out_id<len(farrays) else []
                for i in range(min(n,len(a),len(b),len(out))): out[i]=a[i]+b[i]
            elif name=='SOFTMAX_VEC' and len(args)>=3:
                x_id=int(data[args[0]]); out_id=int(data[args[1]]); n=int(data[args[2]])
                x=farrays[x_id] if x_id<len(farrays) else []
                out=farrays[out_id] if out_id<len(farrays) else []
                if x and n>0:
                    m=max(x[:n]); exps=[math.exp(min(xi-m,88.0)) for xi in x[:n]]
                    s=sum(exps)
                    for i in range(min(n,len(out))): out[i]=exps[i]/s if s else 1.0/n
            elif name=='ARGMAX' and len(args)>=3:
                arr_id=int(data[args[0]]); n=int(data[args[1]]); out_slot=args[2]
                ext(out_slot)
                arr=farrays[arr_id] if arr_id<len(farrays) else []
                if arr and n>0:
                    best=0
                    for i in range(1,min(n,len(arr))):
                        if arr[i]>arr[best]: best=i
                    data[out_slot]=best
                else: data[out_slot]=0
            elif name=='APPLY_OP' and len(args)>=4:
                op_id=int(data[args[0]]); x_slot=args[1]; out_slot=args[2]; n_slot=args[3]
                if op_id in user_ops_runtime:
                    op_def=user_ops_runtime[op_id]
                    x_id=int(data[x_slot]); out_id=int(data[out_slot]); n=int(data[n_slot])
                    x=farrays[x_id] if x_id<len(farrays) else []
                    out=farrays[out_id] if out_id<len(farrays) else []
                    for i in range(min(n,len(x),len(out))): out[i]=self.execute_user_op(op_def,x[i])
                    self.ops_executed[op_id]=self.ops_executed.get(op_id,0)+1
            elif name=='JMP': pc=op['jump_to']; continue
            elif name=='JIF':
                if data[args[0]]==0: pc=op['jump_to']; continue
            elif name=='FUNC': pass
            elif name=='CALL':
                fid=args[0]; na=args[1]; res_slot=args[2]; cargs=args[3:3+na]
                if fid in ftable:
                    fi=ftable[fid]; pslots=fi['param_slots']
                    all_s=set(pslots)|fi.get('local_slots',set())
                    saved={s:data[s] for s in all_s if s<len(data)}
                    arg_vals=[data[cargs[j]] for j in range(min(na,len(pslots)))]
                    for j,ps in enumerate(pslots): ext(ps); data[ps]=arg_vals[j] if j<len(arg_vals) else 0
                    cstack.append({'ret_pc':pc+1,'res_slot':res_slot,'saved':saved})
                    pc=fi['entry']+1; continue
            elif name=='RET':
                if cstack:
                    frame=cstack.pop(); rv=data[args[0]] if args else 0
                    for s,v in frame['saved'].items(): ext(s); data[s]=v
                    ext(frame['res_slot']); data[frame['res_slot']]=rv
                    pc=frame['ret_pc']; continue
                else: break
            pc+=1
        return data,farrays

def make_leaky_relu_1input(alpha=0.01):
    steps=[(11,0,0,2),(0,2,2,3),(0,3,3,4),(0,4,4,5),(0,5,3,6),(2,6,6,7),
           (10,0,0,8),(8,0,8,9),(9,0,8,10),(3,10,7,11),(0,9,11,1)]
    return {'op_id':0,'name':'leaky_relu_0.01','n_inputs':1,'n_outputs':1,'steps':steps,'alpha':0.01}

def make_swish_def():
    steps=[(7,0,0,2),(4,2,0,3),(11,0,0,4),(0,4,3,5),(3,0,5,6),(10,0,0,7),(0,6,7,1)]
    return {'op_id':1,'name':'swish','n_inputs':1,'n_outputs':1,'steps':steps}

def make_elu_1input(alpha=1.0):
    steps=[(10,0,0,2),(8,0,2,3),(4,0,0,4),(11,0,0,5),(1,4,5,5),(9,5,2,6),(0,3,6,1)]
    return {'op_id':2,'name':'elu_1.0','n_inputs':1,'n_outputs':1,'steps':steps,'alpha':1.0}

def train_model(activation_name, activation_fn, alpha=None, hidden_size=16,
                X=None, y=None, epochs=2000, lr=0.05, seed=42):
    import numpy as np
    if X is None or y is None:
        from sklearn.datasets import load_iris
        from sklearn.preprocessing import StandardScaler
        iris=load_iris(); X=iris.data.astype(np.float32); y=iris.target
        scaler=StandardScaler(); X=scaler.fit_transform(X).astype(np.float32)
    n_classes=len(np.unique(y)); n_features=X.shape[1]
    Y=np.zeros((len(y),n_classes),dtype=np.float32)
    for i,yi in enumerate(y): Y[i,yi]=1.0
    np.random.seed(seed)
    W1=(np.random.randn(hidden_size,n_features)*np.sqrt(2.0/n_features)).astype(np.float32)
    b1=np.zeros(hidden_size,dtype=np.float32)
    W2=(np.random.randn(n_classes,hidden_size)*np.sqrt(2.0/hidden_size)).astype(np.float32)
    b2=np.zeros(n_classes,dtype=np.float32)
    def softmax(z):
        z=z-z.max(axis=1,keepdims=True); e=np.exp(z); return e/e.sum(axis=1,keepdims=True)
    def forward(X):
        z1=X@W1.T+b1; h=np.vectorize(activation_fn)(z1); return h,softmax(h@W2.T+b2)
    eps=1e-5
    dact=np.vectorize(lambda x:(activation_fn(x+eps)-activation_fn(x-eps))/(2*eps))
    n=len(X)
    for epoch in range(epochs):
        h,prob=forward(X); dL=(prob-Y)/n
        dW2=dL.T@h; db2=dL.sum(0)
        dh=dL@W2; dh=dh*dact(X@W1.T+b1)
        dW1=dh.T@X; db1=dh.sum(0)
        W1-=lr*dW1; b1-=lr*db1; W2-=lr*dW2; b2-=lr*db2
    _,prob=forward(X); preds=np.argmax(prob,1); acc=float(np.mean(preds==y))
    return {'W1':W1,'b1':b1,'W2':W2,'b2':b2,'activation':activation_name,
            'X_sample':X[:5],'y_sample':y[:5],'train_acc':acc,'alpha':alpha}

def export_model(weights, op_def):
    import numpy as np
    W1=weights['W1']; b1=weights['b1']; W2=weights['W2']; b2=weights['b2']
    rows1,cols1=W1.shape; rows2,cols2=W2.shape
    data_values=[]; float_slots=set()
    def add_float(f):
        i=len(data_values); data_values.append(float(f)); float_slots.add(i); return i
    def add_int(v):
        i=len(data_values); data_values.append(int(v)&0xFFFF); return i
    W1_start=len(data_values)
    for v in W1.flatten(): add_float(v)
    b1_start=len(data_values)
    for v in b1: add_float(v)
    W2_start=len(data_values)
    for v in W2.flatten(): add_float(v)
    b2_start=len(data_values)
    for v in b2: add_float(v)
    alpha_val=weights.get('alpha',0.01) or 0.01; alpha_slot=add_float(alpha_val)
    rows1_slot=add_int(rows1); cols1_slot=add_int(cols1)
    rows2_slot=add_int(rows2); cols2_slot=add_int(cols2)
    n1_slot=add_int(rows1); n2_slot=add_int(rows2); n4_slot=add_int(cols1)
    W1_arr_slot=add_int(0); b1_arr_slot=add_int(0)
    W2_arr_slot=add_int(0); b2_arr_slot=add_int(0)
    x_arr_slot=add_int(0); h_arr_slot=add_int(0)
    out_arr_slot=add_int(0); tmp_arr_slot=add_int(0)
    pred_slot=add_int(0); idx_slot=add_int(0); val_slot=add_float(0.0)
    op_id_slot=add_int(op_def['op_id'])
    W1_size_slot=add_int(rows1*cols1); b1_size_slot=add_int(rows1)
    W2_size_slot=add_int(rows2*cols2); b2_size_slot=add_int(rows2)
    x_size_slot=add_int(cols1); h_size_slot=add_int(rows1); out_size_slot=add_int(rows2)
    instrs=[]; D=D_TOP
    def I(op,args=None,**kwargs): instrs.append({'op':op,'args':args or [],'depth':D,**kwargs})
    I('DEFINE_OP',op_id=op_def['op_id'],n_inputs=op_def['n_inputs'],
      n_outputs=op_def['n_outputs'],steps=op_def['steps'])
    I('FARR_NEW',[W1_size_slot,W1_arr_slot]); I('FARR_NEW',[b1_size_slot,b1_arr_slot])
    I('FARR_NEW',[W2_size_slot,W2_arr_slot]); I('FARR_NEW',[b2_size_slot,b2_arr_slot])
    I('FARR_NEW',[x_size_slot,x_arr_slot]); I('FARR_NEW',[h_size_slot,h_arr_slot])
    I('FARR_NEW',[out_size_slot,out_arr_slot]); I('FARR_NEW',[h_size_slot,tmp_arr_slot])
    for i,slot in enumerate(range(W1_start,W1_start+rows1*cols1)):
        idx_s=add_int(i); I('FSET',[W1_arr_slot,idx_s,slot])
    for i,slot in enumerate(range(b1_start,b1_start+rows1)):
        idx_s=add_int(i); I('FSET',[b1_arr_slot,idx_s,slot])
    for i,slot in enumerate(range(W2_start,W2_start+rows2*cols2)):
        idx_s=add_int(i); I('FSET',[W2_arr_slot,idx_s,slot])
    for i,slot in enumerate(range(b2_start,b2_start+rows2)):
        idx_s=add_int(i); I('FSET',[b2_arr_slot,idx_s,slot])
    X_sample=weights['X_sample']; y_sample=weights['y_sample']
    for s_idx in range(len(X_sample)):
        for fi in range(X_sample.shape[1]):
            fval=float(X_sample[s_idx,fi]); f_slot=add_float(fval)
            idx_s=add_int(fi); I('FSET',[x_arr_slot,idx_s,f_slot])
        I('MAT_VEC',[W1_arr_slot,x_arr_slot,h_arr_slot,rows1_slot,cols1_slot])
        I('VEC_ADD',[h_arr_slot,b1_arr_slot,h_arr_slot,n1_slot])
        I('CALL_OP',[op_id_slot,h_arr_slot,h_arr_slot,n1_slot])
        I('MAT_VEC',[W2_arr_slot,h_arr_slot,out_arr_slot,rows2_slot,cols2_slot])
        I('VEC_ADD',[out_arr_slot,b2_arr_slot,out_arr_slot,n2_slot])
        I('SOFTMAX_VEC',[out_arr_slot,out_arr_slot,n2_slot])
        I('ARGMAX',[out_arr_slot,n2_slot,pred_slot])
        I('PRINT',[pred_slot])
    return encode(instrs,data_values,float_slots)
