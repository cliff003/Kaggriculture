```
STRAWBERRY m1 S>=1: n=6858 P(sell)=0.615
own_sold24 < 6.50  (n=6858 P=0.62)
  |hour < 15.00  (n=2463 P=0.37)
  |  |steps_left < 20.00  (n=1751 P=0.25)
  |  |  |leaf n=86 P(sell)=0.91
  |  |steps_left >= 20.00
  |  |  |leaf n=1665 P(sell)=0.21
  |hour >= 15.00
  |  |since_own_sale < 16.50  (n=712 P=0.69)
  |  |  |leaf n=352 P(sell)=0.86
  |  |since_own_sale >= 16.50
  |  |  |leaf n=360 P(sell)=0.52
own_sold24 >= 6.50
  |hour < 3.00  (n=4395 P=0.75)
  |  |since_own_sale < 1.50  (n=1021 P=0.47)
  |  |  |leaf n=448 P(sell)=0.68
  |  |since_own_sale >= 1.50
  |  |  |leaf n=573 P(sell)=0.30
  |hour >= 3.00
  |  |since_own_sale < 4.50  (n=3374 P=0.83)
  |  |  |leaf n=2406 P(sell)=0.91
  |  |since_own_sale >= 4.50
  |  |  |leaf n=968 P(sell)=0.65
depth 1 in-sample acc 0.705
depth 2 in-sample acc 0.753
depth 3 in-sample acc 0.787
depth 4 in-sample acc 0.798
depth 5 in-sample acc 0.801
```

```
MILK m1 S>=1: n=8253 P(sell)=0.511
hour < 15.00  (n=8253 P=0.51)
  |farm_yield_h0 < 6.50  (n=5853 P=0.39)
  |  |steps_left < 396.00  (n=1794 P=0.19)
  |  |  |leaf n=697 P(sell)=0.36
  |  |steps_left >= 396.00
  |  |  |leaf n=1097 P(sell)=0.08
  |farm_yield_h0 >= 6.50
  |  |p/base < 0.24  (n=4059 P=0.48)
  |  |  |leaf n=1197 P(sell)=0.23
  |  |p/base >= 0.24
  |  |  |leaf n=2862 P(sell)=0.59
hour >= 15.00
  |day < 11.50  (n=2400 P=0.79)
  |  |dp_since_h0 < 3.50  (n=280 P=0.09)
  |  |  |leaf n=99 P(sell)=0.20
  |  |dp_since_h0 >= 3.50
  |  |  |leaf n=181 P(sell)=0.02
  |day >= 11.50
  |  |since_own_sale < 5.50  (n=2120 P=0.89)
  |  |  |leaf n=1240 P(sell)=0.95
  |  |since_own_sale >= 5.50
  |  |  |leaf n=880 P(sell)=0.81
depth 1 in-sample acc 0.661
depth 2 in-sample acc 0.689
depth 3 in-sample acc 0.75
depth 4 in-sample acc 0.75
depth 5 in-sample acc 0.784
```

```
WOOL m1 S>=1: n=5574 P(sell)=0.632
own_sold24 < 2.50  (n=5574 P=0.63)
  |dp4 < 0.50  (n=1743 P=0.19)
  |  |shop_demand < 1.00  (n=1231 P=0.08)
  |  |  |leaf n=1156 P(sell)=0.05
  |  |shop_demand >= 1.00
  |  |  |leaf n=75 P(sell)=0.56
  |dp4 >= 0.50
  |  |own_sold24 < 0.50  (n=512 P=0.45)
  |  |  |leaf n=325 P(sell)=0.30
  |  |own_sold24 >= 0.50
  |  |  |leaf n=187 P(sell)=0.70
own_sold24 >= 2.50
  |since_own_sale < 4.50  (n=3831 P=0.83)
  |  |hour < 3.00  (n=2989 P=0.90)
  |  |  |leaf n=516 P(sell)=0.70
  |  |hour >= 3.00
  |  |  |leaf n=2473 P(sell)=0.95
  |since_own_sale >= 4.50
  |  |shop_demand < 1.00  (n=842 P=0.59)
  |  |  |leaf n=166 P(sell)=0.19
  |  |shop_demand >= 1.00
  |  |  |leaf n=676 P(sell)=0.68
depth 1 in-sample acc 0.827
depth 2 in-sample acc 0.827
depth 3 in-sample acc 0.861
depth 4 in-sample acc 0.863
depth 5 in-sample acc 0.865
```

```
STRAWBERRY h0 S>=6: n=1408 P(sell)=0.362
dinv24 < 8.50  (n=1408 P=0.36)
  |since_own_sale < 3.50  (n=889 P=0.18)
  |  |day < 23.50  (n=491 P=0.07)
  |  |  |leaf n=188 P(sell)=0.15
  |  |day >= 23.50
  |  |  |leaf n=303 P(sell)=0.01
  |since_own_sale >= 3.50
  |  |own_sold24 < 2.50  (n=398 P=0.33)
  |  |  |leaf n=131 P(sell)=0.03
  |  |own_sold24 >= 2.50
  |  |  |leaf n=267 P(sell)=0.47
dinv24 >= 8.50
  |p/base < 0.70  (n=519 P=0.67)
  |  |since_own_sale < 3.50  (n=142 P=0.25)
  |  |  |leaf n=75 P(sell)=0.04
  |  |since_own_sale >= 3.50
  |  |  |leaf n=67 P(sell)=0.48
  |p/base >= 0.70
  |  |S < 8.50  (n=377 P=0.83)
  |  |  |leaf n=73 P(sell)=0.62
  |  |S >= 8.50
  |  |  |leaf n=304 P(sell)=0.88
depth 1 in-sample acc 0.763
depth 2 in-sample acc 0.815
depth 3 in-sample acc 0.815
depth 4 in-sample acc 0.845
depth 5 in-sample acc 0.848
```

