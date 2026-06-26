# M5 Falsification — analysis (350 cells, 350 encoded, 338 decoded)

Models present: ['gemma4', 'gpt-oss-120b', 'qwen3-30b-instruct', 'qwen3-coder-next-80b', 'qwen35-a3b']

## By condition (overall)
```
condition                 n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     70     64%     0.848  0.299   27.0  1092.7   28.1     31.9
json                     70    100%     0.938  0.105   37.6   747.9   21.9     40.1
json_schema              70     97%     0.932  0.182   50.6   642.8   17.6     54.3
struct_english           70     99%     0.928  0.155   35.9   790.1   21.5     38.7
fipa_acl                 70     97%     0.915  0.201   42.7   976.1   23.4     46.6
```

## By condition × level
```
-- Level 1 --
L1 condition              n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     20     90%     0.890  0.300   18.4   754.4   31.6     20.6
json                     20    100%     0.968  0.078   25.8   509.8   23.0     26.6
json_schema              20    100%     0.975  0.075   39.5   424.4   21.3     40.5
struct_english           20    100%     0.988  0.054   27.2   648.6   25.0     27.6
fipa_acl                 20    100%     0.988  0.054   35.8   959.1   29.1     36.3
-- Level 2 --
L2 condition              n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     30     57%     0.860  0.339   30.1  1064.2   25.0     35.0
json                     30    100%     0.937  0.103   41.5   854.9   24.2     44.3
json_schema              30     97%     0.953  0.184   54.7   697.3   15.0     57.4
struct_english           30    100%     0.910  0.135   39.9   790.5   19.6     43.9
fipa_acl                 30     97%     0.960  0.182   46.2   911.8   20.4     48.1
-- Level 3 --
L3 condition              n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     20     50%     0.787  0.209   31.1  1472.9   29.1     39.5
json                     20    100%     0.911  0.121   43.5   825.6   17.5     47.7
json_schema              20     95%     0.856  0.225   55.5   789.6   17.6     64.9
struct_english           20     95%     0.895  0.222   38.6   938.4   20.6     43.2
fipa_acl                 20     95%     0.776  0.246   44.2  1091.9   21.8     57.0
```

## By condition × model (size axis)
```
-- gemma4 --
condition                 n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     14     43%     0.733  0.396   22.4  2373.5   44.5     30.6
json                     14    100%     0.897  0.127   38.1   528.3   11.3     42.5
json_schema              14    100%     0.947  0.092   53.2   968.1   18.3     56.2
struct_english           14    100%     0.950  0.101   37.2     614   12.8     39.2
fipa_acl                 14    100%     0.963  0.089   48.0  1152.4   21.5     49.9
-- gpt-oss-120b --
condition                 n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     14     71%     0.947  0.105   31.6   342.1   31.5     33.3
json                     14    100%     0.950  0.101   40.1   197.8   35.6     42.3
json_schema              14     93%     0.906  0.260   48.1     268   23.4     53.2
struct_english           14    100%     0.964  0.093   32.9   259.3   26.4     34.1
fipa_acl                 14    100%     0.941  0.135   45.6   339.2   23.4     48.4
-- qwen3-30b-instruct --
condition                 n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     14     64%     0.914  0.111   32.6    36.8    0.9     35.6
json                     14    100%     0.950  0.079   32.5    36.6    0.9     34.2
json_schema              14    100%     0.954  0.077   54.6    58.3    1.0     57.3
struct_english           14    100%     0.908  0.130   37.9    42.1    0.9     41.8
fipa_acl                 14    100%     0.920  0.137   41.1    44.8    0.9     44.7
-- qwen3-coder-next-80b --
condition                 n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     14     86%     0.960  0.079   30.5    34.7   14.7     31.8
json                     14    100%     0.945  0.115   39.1    43.3   11.6     41.3
json_schema              14    100%     0.954  0.117   51.2    55.6   13.3     53.7
struct_english           14    100%     0.950  0.101   36.9    41.1   15.5     38.9
fipa_acl                 14    100%     0.936  0.125   41.3    45.8   12.5     44.1
-- qwen35-a3b --
condition                 n  valid%  fidelity    ±sd   ntok    ctok  lat_s  eff_tok
axon                     14     57%     0.685  0.439   18.1  3309.6   56.9     26.5
json                     14    100%     0.948  0.083   38.0  2933.7   50.3     40.1
json_schema              14     93%     0.897  0.257   45.6  1929.2   33.4     50.9
struct_english           14     93%     0.867  0.262   34.8  3163.6   54.0     40.1
fipa_acl                 14     86%     0.816  0.357   37.4  3685.2   64.3     45.8
```

## Pareto frontier (fidelity↑ vs neutral-tokens↓)
Non-dominated conditions: **['axon', 'json', 'struct_english']**
AXON on frontier: **YES**

## Falsification verdict — does AXON earn its place?
```
slice                      axon_fid axon_tok         best_inc  inc_fid  inc_tok AXON_WINS
OVERALL                       0.848     27.0             json    0.938     37.6        no
Level 1                       0.890     18.4   struct_english    0.988     27.2        no
Level 2                       0.860     30.1         fipa_acl    0.960     46.2        no
Level 3                       0.787     31.1             json    0.911     43.5        no
model:gemma4                  0.733     22.4         fipa_acl    0.963     48.0        no
model:gpt-oss-120b            0.947     31.6   struct_english    0.964     32.9       YES
model:qwen3-30b-instruct      0.914     32.6      json_schema    0.954     54.6        no
model:qwen3-coder-next-80b    0.960     30.5      json_schema    0.954     51.2       YES
model:qwen35-a3b              0.685     18.1             json    0.948     38.0        no
```

**AXON earns its place in at least one slice: YES**
(earns = fidelity within 0.02 of best incumbent AND strictly fewer neutral tokens)
