# Kaggriculture submission, team 42 (Kefei Yan, Frank Yang, yirenw11).
# Base agent: cha22 agent (Abhinav0370) (Apache-2.0, upstream notices retained inside the embedded source
# and in NOTICE.txt). Modifications by team 42, 2026-09-25:
# 1. order-slot priority layer. From step 288 on, each turn's market list is rewritten so that SELL
#    orders are issued before placeholder slots and before fixed-price orders (HIRE, BUY_SEED,
#    BUY_ANIMAL, BUY_LAND). BUY_PRODUCT orders keep their relative position. Quantities are unchanged.
# 2. day-end room guard (True). At hour 23 the projected shed after this turn's unit actions, market
#    orders and the end-of-day inventory drop is computed with the engine's rules; units that the
#    100-item cap would discard are sold instead.
# 3. eager sale layer. From step 288 to step 700, shed stock that the turn's orders do not
#    already sell is sold on arrival while the quote lies in the band (share of base price):
#    MILK 0.3-0.9, STRAWBERRY 0.3-0.9, WOOL 0.3-0.9.
# 4. sale ordering layer. From step 288, SELL orders are permuted among the slots they already
#    occupy, largest same-step race stake first (the market's own price function); ties within 10 keep
#    the base order.
#    The base policy is otherwise unchanged.
# v12_4 (2026-09-27): the embedded cha22 source carries one change. Its V219 tomato investment (day 18,
#    south-east quadrant, 10 tomatoes) needed three pizza / farmers-market shops; it now also qualifies
#    with two when they open early (tomato shop-days by day 18 >= 24, i.e. days 3 and 6 or 3 and 9).
import base64 as _b64
import math
import zlib as _zlib

_BASE_SHA256 = "ea87e3cb780642abb7501f03ab37ffb430b040d6be1d736c26e6a3fb68ac5718"   # upstream cha22 127ed3e6, patched: see header
_BASE_SRC = _zlib.decompress(_b64.b85decode(
    'c-q{(XLsVvvM~Dntabi_FgAx^Jmg@q$vFpm?f?P=2!w<sk!}C>w}T`k5FS5!@AIyE?>u2ZbXQkbS6A+qktmY08BdQljJV+`LfDK}v>?zNOKgL`+|R^%Gh*m5'
    '(QyX}b7D=7=ak*`<ai`lPNc__K#VAc+gXS;vk?e!PJvzoLmntz`0xKR5{*PMUF#7uQluWy7sAX_0>y7h5sonBxfLOZ)S7SxU5~_^<LM)K>~Rpkh!x4tXqIrg'
    'ERRI8+HU024e%k+XjEGS$xet|x{-oIkn1(YPN)e%ifDZBh2W;(BP|e9nxURxqjaxkclzA~EpQCLh2TIRnw`NxmXt^c)cb~F#}q-c!kXp*u+f1y%*jK*`Ae8{'
    'Ydg<vM2fdNf=;JhpjT^#QWL|1#?aCcjp*|eV}L6?0b@Q96;8zD6-9{dM&wq23}cdE4hTR(6nT2Ifs}a$_=8^sQ5er@c1bah5;~8>gc8INAR_k&K=9<=|44|G'
    'C~QQMr5_=fHNO?;1IZ#PrNC%BO%qvWbDVJ7C*q7XfW*^yA%u{!oIE9xGz%#J*Hvd?TelOe4w{}9jGdUTK;svR2js6FDgKdYQfrY~jVPW75-x|!hhQ`*h8n|Z'
    'uc+}HU@EMhi80Tu2bjGE91pMoB%*d;4JH&?QdT6!96P1?73LNiV)wp*>w{p{B+hiXoG-t?|2;`CcW$y7!`8n<dIeXQ0h1wT)U!gCM->SWm?}>LMk5)50;6#&'
    'dMqHy(X2?#cr<e8OqI=A5P6DR0k~s|6#&7e9CL$Eu7E-)&yNX}1k{;P!n3rv#DqN9AxjG)$Aftgvkl2lLYM1Gtmg*-vJ&70euZWOSY*7R&<>f9Ye;&L12};t'
    '+tK2j@Oi-c<HocAmYx7?y<spnJYA9qE(?jsN{Hl|!URG~2Ed{XvL<OB?56dz{<d)hugHE$Ebk+xl_&U2G(l(3DWF=<M?xUMu45>2@_3%)7zhbYnks_Y*sx&X'
    'DFQGV5MqFg=TSqq_mr}MFbse-WF0t3N%~2X2m6@3HN(Io6lX_@Rjn&{rYtP{@2`I_wnPat*I&AHfRKe)A#q$FS-=?wFrLHnUB9^~uAhJX+U<5vBpU3A<7dBQ'
    'ZvLghw3Tj@n?$0L0^+xl%D3{>N|VS`8$`RA2EsgDYgAM1Bz*jcTBY*MRwMt?hEG&roKHlGngTAvtfeKzoix)sz(qg~0_gzc7L?*}g)y6fO*z4R!B*pmjQ}(W'
    'PpKH=3=KA)0B)A0C_xH<$){MH9l*MbF&rlt0xaBY4mO^wDkj``vjQSVA3=`4!f?#34?uFvMS|P0V66depgS!dpkzmy42^mQrPoQE18D$82ZDx0JSU!4{|Xao'
    '1~@*A#<;>}!@~KZ$xw(}0W29EKo!vT42c76BxGqyz&HRZi#!Lm1j$qK7Y0q>5zY)g-2joygWpywjy(gD+G3%CK;dDZhz!RgY}Olo%|S`2kXm5})!N-jfbP(o'
    '1j0;PaBpr0W#t4&{jms90qOyLeuVODOagv@?aqMkuZS8@BC$Yd!gYnC3!Cv=LJvs6Ifdu|7y}JWBJdYf+R>2R03b6B@Ih-P%;_}*Hl?S4xNC|ZL+EC&<H3SP'
    '<N&GgI;dc6L_vgx09X~Ua6n$kKmpVd#R7tiX|TAO0aVytvcfC3xg*Q~0{q0^S=8JB{)Hsk(vuB@$P;S5Im4j#0CQS^7_Ff+MJAubh<Ll8wYtHJO)%^j>{_rR'
    'SC_1~=BX*gL(PDGouXw}B5RAA&|s!m$*9(zX2;A15eMvBXo&#r3iKORSpqi|caZ-CG$vTA30M+&yCPU;NVv_TEI6k0Y{N^YCNKrBq)&CU0K9TN4U#?JXJDm('
    'f`XVKQ&lovfSy%tYd|ppHYR1JLr)m#>y#h~Of3ZQQ9Ic)n2TA1ZMLT22ILTm(yV8IRlt0}W6k_8L?D>>7OMsUg2LM!7#}oAh==tx6}lY1yb>ro@DO2-gc;<?'
    '^OgZ-xils9hQY*?X1O9KKn`t5njuGwEIU-f?Gegm$fsjcVmDGPQ)DTLtx`oyV%kyAI73oN6rlz~1e0+-LotJyP<s*?>!2^t7+_D}zOZou`3>}5a$qirl9G($'
    'Ek!{32zQtK0SD73iA0GrFiaA85+hQ8>&l`HjBIeYRRDWofd@xJ%Lq5lZcdNqT3G_t5txEBvhcPvT4l)ZfKt-FA}By}j+egyC=v&#ci$Nv)TO{BV@0$iBp8xo'
    '&<+AUCByid7p|qdO4v;`qT`XcB&9@2$nnyGq7fub#8WF^YOA(1wI+GQM36>kJ}Y2%G6!hdFA)((fRP{zvE+)f$jkukcYaEak>YvOs$qr3SExZsQQY*B8<J2%'
    'NLGa|CtPk7WtVFQR!AysP+4Ou2tjz7g+hEjkt`q;Fb-1-bp%arP2^FvcSNX6I2QVwD)K50DF7)OJBatt6cCcqjzMD~#c*ZFs8%0o)NhrL+CYK=9$^4C#E1ff'
    'odTMCYc&1LvLNo1ncbbiVcS9x@1P&@OL-0m^+&iUBa%TZw&P(}7MVL6R$2@KZj*~Opw2{tG!upMhC<6BJbtU*)Iv`^68QIw8IYzlgPmF6y*#Qlp<;gt2LU)8'
    '!i6dTYJEdNg)~MASZaiM0_s$3A1P*@dJP`6Vn@RoD&j*L0-Jlh5d_(1qE|@PO4e)_$w`f_qxLdEw3C)u70gLk1J{t-2w<C|7|leHW6&g1S$mW~&sd~G0GGm5'
    'Lv+?<QYhc<U=W5R)cg7A?$&0%u=*7e$Q$)1c9xo?P`0ivMkj!y3R(bG17<6QbOFF#J(Omz;z*Uqz`@5HSOIJfK<itzOV#4b^+aT$Q3uCQDg=@3I-<G3YFlDv'
    'UB64aA=RRt0{WLw(Tjjm2jGv)NMwBg0~O2|n3!uy1cXxYClH&=WJg20hUHj0VhRBe0DiRtJByz|Pmep0jCin5c?x`^fmylb#!wsRSqqXE3x}0GM9>NB#x>;i'
    'D-o$t3)s;IbOp@3W=OCflqUdrtic8JL^5C0zUGAsqDXUO!e5Q6V=EwWq+T_*YSn5al-&P+S~4@}Nv%b=A%R~c%0?MLQ^3BPg;?WBtCkcv5dhwt+)~K8RH21p'
    '0^D>8O-!IqC<e%I{C^;dI9|l7rAQCSWS0z5B%f4Mgyg^rCy!08*9>%&ITkPjB07|N5`trfqyhPHTkR|XQ4t(9u@%Y7g553%Bu}HQJmrDdlHD$fR_Rl<tS}1}'
    ';K_3=C23h8J%Q<?I2x$uWe3&Fu!k<`aWD^TTxwC2M%lrYk@e>jk)J}QP&;e_kaCdkm1Pp?8AgPhk??0EAf*U|`K$reRzA-Of*sKh&S%VRpv8v219l(@hTI7o'
    'T7+|Es2SELQjou^vGk#w)C$$_gd<Wf7=1yC7HB|?&&zd?=O?ew3faj361M!bOsX=^WH(ycO|tuQ-iMMJl`S}|Wu&mCsNx|~kWECGLy-AWA-0s`n5adE=ZR=g'
    '>M+<7!eK=o&QkGGd;u9s%XZYIAp6F;MC$}CRxsXXB}JB@^#uOr)EZyw`AhM2eJS{O_S6u4G>o^RD9ivj>W)naS?E1$^|+a|;E8VlH_jmL5LN68fkmgmjG@3&'
    'Ti|MU7XG=KH;J^(rHd1i)wF8xk!o-pr8=AT(BFgM2pqxUA)5i$hGrozNqHD89#BXs{13s7QI=qWNdZCWp)gjVfD;&xvMH~MNFdJzpmsS|Ee6WSXQp|C`|_-P'
    'AEn*!2*vA!f>zt3)_g(ye9mzxDJK+K(ZNbbI%};*EQn<=2*nA93~Zph;Cvy0@jm56jY^bVi_1ytk#S;y@=xIr$z_GSa963e^2zia*tmNUtpnVz(qPaR&<?2H'
    'lPV#iv$?KljTTW0O?I70u(sp`Iml<;q;v@lB^yd(X(37S5y=)jBQ%%CpHNy0NuTVxlt!!wz%UdkK<Dow*&+2hZ*yRijbU0$LY9;<J(K=StxKL0zQrV@RuCE%'
    'ypRUkm>WS)&yosi<=I)oUJt?XkGe!BWqVT<+mpN(9g0n_Hx#m0fa8jn55VLnb~xLEvRW*RO#+`EWy(q5KDXxBZG_@am+C4eK(-2w1}HI3;N_e>Z)g);AtmiX'
    'B<&8GoQ9%`$jJnL=Amn*W>zgAc@7e_ezH{_@nQ&IT`nev96%VenM^2lvRTOnw1$&pS%lqId4Y9=A)>b&nE@ox-Eb%_2i!YsbMPA-*2F~mKKG+bw6ouXY-p6^'
    '!1l&PtWUc>5RNo0HTp0XNkbD_V|DAe7Mif8PC5=lQYGQIsSZw$n%y-;p6=m>zoZUJDmxB=grjRCnP)Vvl7SjUulNEm(2lHo$YPgqC&it*@KSVE$&36lxpW5k'
    '+Gl%Icp};?(9!~0Noo&99MjN=M{rfCCUx}YaB0%2;&-aB-OW&)#u0(zUdF4i(K%8_=l`KEDcN}lSrso~DA<&qsPew}PlXd<KP4fCwAF~iUL@S+Gvty&jf4;s'
    'HbAWi)P%z6HMm=}>m&__%@`am21Hf7w;Aw5(dIZvy9l|E)Sen^RRxmX3UPR9M)Ejecj+K$5-2_(Pi1>YfU;F(<4-swenspKsPb%ZDWt?Dww6?RAaVs`hKdaZ'
    '!+jLLg;@~kD?m=-bKF>FY#H@OO`uJ3v*p4W#4f;K5Wqq~lL0L?ur0V1EFOS30lEY0W(+1PEsokbg3;@%n6<p`<i(V9i;gx?6VCrcq-X)TdoX)GCAz>824p%Y'
    'dqu%{bih71iXuR_P$N9h0wY)J907bhFQg<fgfq@&h%^j?=y=)c4ltOjS$7MJ<^ctAmuM3C<{j~pXy%(La(DBsT(#XIx`{?3QEBDVO`_URS5H(kM56La6!Vo7'
    'u&!vFhu_0+v7ng}jbze96*@leH55B0Wf^w>t~w$ca^HAeISpvr%C}1CN3awXd%lus<SW^9IbCTz66JIwnFF{cUh<`U>lJZVCf};0o4D2^aRyUMG{8c(ONj<i'
    'Yd31uW*TdAoSS7}Mg~k|4Th#swgzRlqza=;P6Erxb8DW49s`>E6!0Ewg}C!9wpB4?9CZ~0V1mJUtHeGnASEGiV_Na|v3`(}+$cz`&T?P-<7&<fJb|Y&kzv;o'
    'O^#>=6*c6cawmYn#fk_a3<*49Q1lld%kc+oI7!YA0^SnUp%9juG4u?U9a<ih5`;%hoLe2^`s<!BV~Yf4K^S_3Y)ORT48~d1DIa-Y5f+LFsA@rf4`KPM(L^xt'
    'q*_OYM#D>C4z%RtikxY)9uR<BvvIE85Y`l|dC-;t(6H)HO2I&r2}iqOvQvU9i+LDq1lYr%K98#ypp~Gu1z_U-(osjm-6)c2gP+i>w7e>@d=UdNe_Ns;;|Ax?'
    'aG0HE95>m~%tiEc3G4XQYZAsuq2&RK$A~FOGq45@6-qGE4SP1EkYd%Z-+`$U$lYq%;Nd9&Fcf4_=rCMHAkScw!~;3m(kLZ8l`3w)E|CZ#m!U`_sCP;5iAap0'
    'dVxfdWj912aW({08>c&m-h_5<>m+5rO=Zev@OaK~I3|pOzL(_>C=Lxw#wmrQ5D=3HPZAdRq6w{WP*{?j2gH@siiKrCnn)lfG$T)f;6{uTctbYQFDR^_0gf|P'
    'U}A7jNlqXwT;|Sz^ONIt&{xC0uR=UTVHNE2L{Uu=%V^U{iUT0!l~8P3dJN_8SqdYpkyUk0Luu5)IUuIu5Gh&?9Xoo8B|MZ4SU4a$P1SUoP*dPd;ZDFtpXekQ'
    'NPdNcmu%)M6xHng4bPu5ky2P4NOg)w)zUbs{CFKv9~~rnMl-Vmq{f-VigU43F{;X9RWMR>c)F5;8e6XpQq?L^tAU33-ZNZX6!`#R`5={;sH-{QZwRg3MTQR6'
    'TK=%xqg3;v4UVWReGcq0evN9}u@m}uj!H~vikS!m&^SO!U==cgnPCbr@ZIk}cN$L$hFc_6dXO0oNoUDfRmB6I2y=>K|3|6j&~9sa2!n+{kq6{v3&50NV2$}1'
    '8_9D~Sq9qNINV#p0ceN4l7dD73XBF2FrY6Zz|0?RErpL&IsrAuyakvM+RoTXMAq(FR`zmUdqkbfjZkh{g^vLH-T^F8kROWkJE(uOIcKSM2_g&llU5f=NQ9L0'
    '-b(!G9K0d<@f=nUsQKiaz5RUvfBq1^(HsEI7m4mas!kFYO;k>vmcJg=b;N`jHc+Z^Eg=bt>^ebFf;FU+d5~QUnw30hBxMzrQ(IT6I0iRDVM0<9v6T6p6fer9'
    '|5CDC0^UWXnT93as*XSLA#RyHQpKSJNflSTu49847<Geh9E5+<JCL0MnU+n8(jX#l3S?IS)&g^6XB%{60QlBCds*pu4ho$;3gLQ!V7R-xJ8iK(DtfmgA#so^'
    '?FsW5{!}{vF9jCsixXgkA}s<->;C({5`-0XvqFlIFez`B44?@*QvkWZ?+l`20SslwyIQKd2dZ>9Jl#!!9-;WVXW}=vek7irp8h-%cXKcg0X|bblzzg8d+=}Y'
    'tO8KGBDH!X-o=B|=yNy($f0<sGz&Z_yp<7JV;K2n5&IDEs1C*3p#cF`f*1~Q`TuZ;1j&vk*U)SH@Bf0a3m9{SnrVzI8GIy)FeBxtI^hCCIbgSd;UQaYX%YYx'
    'C=oKEFdSN*A?dKO#!dz#FcDaFG5?yJ{1SO!FhY5cC?N-Vz`zW8g7d0UDg$YN5yveD3^$|477Tj__P_uZNzlAH_m$7Wup1@k;YJKM2F6&e1bFw?OFLgmJxbJ)'
    'fGdY62pb@sutc0F4FR+919)~ra~1(U1>OkM2O_op9|2geFd@fM_)Hi@^2|Zq{)|6?fDPc05NU)d4{U+~pvCnFBWenZvQhmVF#TYf4U8qg%Fzuhv2CVHC3ys3'
    'SuR6LvjLbMD-AH(OlFigK<97H0|0AXvUvP1JHi^#3BU*20WuXZ%QaIF=>1?q9tLV~PxJL!8inV$)#Vrjv7`WC0am((BSbI=^CokslwEH9Lmua~kiY_!w^|P%'
    'HPq+;skOqhNBcuz9-x62__P)p^ETKCS_BbH_=@QGDPl#qM+oQ(fwe}N3i$hX*viLy1`G|P_XI0R%oEWFkP?As3<K5t!nm+5#%gX+AW9tb-~W|nXEb26DRhAe'
    'Ge8UHW##IHB@#meirvzHu~sNk?0j;&p8P;Gv)h4l;C2oCPwNBRqQK%DDTf+=BRM79{rSEALqv$v-3qYM;SR_n5hiNyejon)-b3*uiL>AP$HQ5W{YGD*{KBNT'
    '`R8uKLPi5S_kBZ7Q0)#J1DFt$Fc3MwVt1bq1RC_2sK8xirdDh5U?Dz$hOZ`z>C_$gc)D8xc?6_nH=Ry>B&*fhM=jB8wHxUVwATSpcu?=|*Bw|OAk^-V=={8z'
    '^%{9?)E%BQTm}I11SRe>!G6MeOdv|2q&`7#(leTckra-nDI~*BpGYcS!ImUB1}*nFKv)o!M`VhP5eW3)8h{AwBB{GVH+X&vjjD{9n4xvXUKipwfp9!M0fvJC'
    '0Kh{)Ye9z{1!9R*wUP$y#+1UD)S4E!3Dtxh?Jf&eo&Wt`D5o?SOgB(@4hB+DlDcLaGNkkrT14=xbh@eua5mp{bLm72E-ya+3O}`~<wUCrKQ&v8ME51#XuQI2'
    '<#ef9fgjS@Ec%`=72)6AYPAIa&ZHZyd@28yZrp)=&;)Bfs5M}G7SaZf^GrA$=dqp%m*YI%GvRe;$AqmN%D~S=zyWBPsN~Cu(jZxFwh-WKwc1RBAKj>Fvf2fo'
    'J?L{YmrmCZSXDm&9?TuEpr-R3WX?OK|DD99cPc2#GXM)PuQWGAM1Z9O9>;_K2SYo+?90^-`t5XAsWw_U(BBMxv^y;jA~4nDC+I;MK!)F)kAwq$@22s0J9+@d'
    '%QUK$)}Ya@4DzjX886%=_4U@u0#R+Y28m<~Ogvp9kca~ukZ3mHLtq;s9M9$toMrP)WBq9D9mvlA{a>kcCebbdpy^gCU&*4GVySX>HYY&y7Qdk+adW4#1ulM3'
    'RQSbnMe$xdS1Y)SpUz6|;s=$Qy7=X+X)b=y(-qn#Mnc@6WQQPQ1_i(XY(^H2;&&-C1Tt$dhAsv?VTbuz?!p0N2LgSh@a~WvugE<<xh!ZNBhUk2Y(q^CH;_l^'
    'K(lCi10=BEPv94{SkM-?|L6V?bBbA`L--SFN({hCn71SYXaa1B13W}NC4n&?focJ3Fo4|MT?T4Q6gCm0+&Vs(fdacU)RfSo#3nk?1eWJm{3YkTDe0(^@PvdO'
    'a&xByjLixt^d^rF;mAYcSOX*%fqs30c&ZVU3<B^N%H0V30LPPI-GT35BcWL+LqaPZF1H!?(isc?pf}LDfqIyWhVUOmRiG1;SxE$S$is>J;d)@DgEXAvJeymG'
    'HI?Rh7<=o$pV4O>#HCSGC`{>*nU!0TkHiQN2?!*oWE6vS8$jQdhvj1DhN{M+M_}dKh>>Rgq-q4H+y>m#tkS147#?`h5zJhwU!kf8eeTXH0^89z6AG8=dR~Z<'
    'pp|wN&{G}ga8p5<Yay&)YXRhMHH0=YZmFIR+~wqCLBeyJ<~1h(I>6m6PYU3RP9~ih7qv0Nvlov*l&paPiE<_k#loK~M3``0Pbot(@SFnn-Iyt)G#rKa^^0(6'
    'W(h$2cKm^hWJV3`aQ)yX3qF7jes=2qteO)v@&=@6M#kPF?4!?y`$yscFro3p!LXJ`<%{!=<!TZL9yVBiz_5=*9{9BTTg)rloazlE3|Nj^n^EFRL^Wr?x`P>S'
    'U@D?{Tr3U{El{$<v>Gej_JPcJ<Xwz$^%;y?&sga34Tk_QaL&yu8sa1n0~BN(Y*<<x;Lw6aBdy@VgXh<{!$I*wZVd<s+5qC=2NF#&Js+j@QXqonVCj&dp@KRA'
    'ohGms`r$XX{&O`VM8)iY{@xyN_+$^b3^Nd93iSK{pC9Ds7WI&k2!U;c?`9(J0l0;4Zi-8&sRl5?uA!O{<)r>-cbM_<zU?($`DC%J2SW|ws#7VEOso4qzd~9F'
    'xI3n3H-c{#B1$+33hX^3YE&JjxDQy3D<c!1lv4IPW<;c?i2vu>4TG(bu)*!H`(%M=UIP9NNBncuLGq(4P$pi;LtW{Iwge7cL7@kh-tmJ4_(6X_6NnO`u(Ub9'
    'V;HboAyJ?J(Ipmc1<4_61ucb;Ie<Z2ED)v$0*rtEj%2bL(czIwOJ@RTimHBE;z*+AZ;YfvI%(K$q6K`Z>tPWc3<_T8$OgwTX7#joz+vXW&cpt?<!Z0w5{(XW'
    'GxXP6qSnQ7ORx{nmP4XWxVw$L;tu|71{X}F_9kzSk;-SkSr&Oo@Dg7LPV*g#G!A6X4}X)LJj>q~`+B~*Opdn?!oZ@tQd89`=@CNq&~MQoSuK^)z`;`y?C)5h'
    '?^-N)@CkS!{6INdufsOLb5H*(lN^)R%&3t9@E@E#8+2%DcUH>DIYq8vdI85k1(sY3a}E_+z>wbom-Rt~Ed|11&HB06R%NzfeJqC;fsHVLCwd11uu+-mBcU<y'
    ')(F@mF`mxUtbpQgK$t*_P0uXE@wrFfCL=QZRvSKWlqc8#^hfP}<3W&Uz#oCeg)##DYQYlX^mzdR#=;l{gcDe8Dln?v(Fox}!tUJUFW{vxo4(yG$KW187c{pk'
    '#87xNLY$V*1aMwqa07cWfNi0(uzV!8r~(j(6-+t_<Rf;E)sQVuP^SoH%hecAq=G?ofuJCu8p=gyu$^Gv->5S!wZTQMNFZFmQwI>$E2=W6q&wbp2_}V1Zqo|~'
    '7A1;Fq`E;V4C@?>{0XU0Y#8zh!;y+Yk~k2eCxwn3PYwhL{(S)fndtK5)O~TZSw)kJj@X)vAZ9y5LT$l*`mGLmTy_Qap;Q_S7V2tXDNZH1<$r*c`Wx-UH74Bp'
    'yo~BzIFfZ^2~k5;XdBK~rNLEDRN-&Q@zcOiV&&4r&muw%MK`p5M$Dp?Pk;d>(L_)7Itoc)>fhjZwEbyh%qwJvzp3`Q8u9=UMFtNzNDuyIWmfNG9g9!eJ}lzb'
    '^O*k|Q70*lDr<?PbPJoJCmK?ERmz+Szi|T9{Pgr>`2##PR5+j{O$BmFiHBd(2F9A>NhT2npjge%#0fna(358*`JwJX*&;cotX$#-16iLcAiN5Q5<Jq#38>T_'
    'ak0K+aoMAUJlrGB3s117yOFkm5JE7wtH1!Wg}2fGl_|-6<n6;!3<2dJVAUp4jx%xvv+$UQab{RS7iRW(RICh__$uIQ#*lG_88osfp-_wL&8iZe2;f?&h!T`K'
    'NmbUA+OKh*P0Gv@=5yi|=1wijQh%ew@zP0u^AT)c%X5>yYB1BpDbGq4a{!Rdyu9dUn6t<H&cl^KDSR0JLQQW;VTlVOGCM%iiy>E|2}#^ygJ+btHq(%KRmfPb'
    'Bo2_JvMRh>9-XF7n>9S=YgQIoS4V1BEuy8>rL2|=uE@1+o6zKp<>2Ly=;u4saxewVJR-+S7}ACb8UU9+XrEpJl2cnazYIr0VRxMPr6+K+NQuDT_;w%ZKp)G>'
    '+4pzxpt=lJ{G$j$ES{uuGXJ)GQgI}LDDk6gN5a81Tn4QMH5E~O8h^HELJNYZc4g2cfFbTsz5tg%5Pt&-3nB`r-u=07`q5A)RfA^&CYJ6H4ey>M9~6J(G4e3m'
    '`Kg;GzC$-#u`}F4O5G@Z?j{>bGX|_@fkj5B`RC^aVyfvYwlJKHnoOFRp<k)>wWbm^A_0p}EJoCF;d&X+CXT50JXRZjG)v&XM25sh$`wn3%g_#Z_!~C*bDfA#'
    'p$e0*PZNq-!w;%X*AY@}OI6BFV<f2ehjy-5Nng$wh|ij4du&L2lL8RP!y)VgwTC3uq(n8)bx^%fYZ&kpHq$A+hsJ@Rig03L!a}2n&c;Q|jUZ}y8~4zURsCRT'
    '(1`=d+(K(|2?67CS_A3e_(NEMn+o)lQ)Mj5sqhQVL<MiE<OU9n+tGiQ>ngX`z<bu$)d-{C>p#Cm$jaw$5UW4>U{U=b<`eM`qND6t$Ts6eE=+1FM;Vdz_xsNc'
    'grH-OYqBAMpo0&Y;toB6ROOH#>6V({WC23^`F0Hno)&D4=4p#)+(GWQ>yO2vBM3AMBQ3Q|q;vBz$H)&6F_7u1vvnA}t5DL8W6qIn)h-6lCGt2fR07l^1X51K'
    'e?%hyNu(EJ(A*+<Wrs-K{EvbR7kMI_K!b;q&KVT*9lW>%-dHGVf+B#8z_ekl61<ZH>SB0};27QF0$E8di=pb#&)TVi2-q%++{~Qe23IbWq7NnYsZpG&^+z_3'
    'Y}1^dZ)pl83}NiZd^3_Gud`yGYXl6hZ<+trs>VNB5r)CwjD%WPT`q?_nhfsl4_5A~ubTdtGjCXeS_LTskc>=K9u|8gGGR4pQLPYFL_uj+t>%%kSt>cNN&LyF'
    'ap>5qYCrTO4o2hLNCN$cR?ngjQe8E28>Xt21}L1MR{86Xa;`x6qeLmr)hD;d#YsQe%7Jv1M~4feGLHV}4u7sKl-Edkg7RkH5eQYOp07cb908^OMQg}N5Km+Z'
    'eru&cQ_$@jOsJ6vA6(7@tDtiW6pH%%D^+h&P-%0qZrbT-*6>l8&5hMmtsK59?aH&ciH_3sKY-39=>YBJmil;W>Y8qoOx^4P&A)THszB=Y2<Jxs7{0pB>h=Jt'
    'R>}ysSXYLus?)j+_}u6Ma|QZOCZSvTb$d{~=GW8G9TB(El%ZZe`u&WNQdNZg`J?Mw;GXB7q>_p>`U}4LL&xk=dFsEf+;n8UId#VZn&QH0LY<%0#|i#TKU$?I'
    'u=S*oh8I2!DV->TeiHGEP>wFhr!D?Rz-Jav@JW4=f!(0@DFF8eg+$L#FOM`l!PM;&pr*)^(us(jeAEnAg(&yyNTnkrd)SeOkSbq5<Eu=8AQFfLygZAZKxrZX'
    'BOJ~X-zJal0;DIjbg=-Qwbs>AVr7bP4Q)k8mvaQ&0=*U$yJ3{2+?50r33D7DzfM@8=TAUl0hizWTP_W~to)M3S1__8R8U`w#iE8MGd3O%vO4<o`&sV$N1vnA'
    'he-ZCj#8Tm*DQ5yENFQw4=-F-9a0%s0cY_ucx{}N8YWSt`y)Ew!g4#LeBL+IhElGLX3>p57Y3SgVINGXhfrJGOFlBh;X4aq01;W?N{tfi03Oi{qc#cgX&rRi'
    'Bnnc%yEmaXEe)q|EeY?|<kt9P9=<FJp3KA#Y1LLh*uXAx8o@&xizopDaHvcH#^-5xoy~^d(pw5_l!VlRmacNblTlA!GYzmo(Rm#;rc$<@Bv$AS7XfeE6_^x>'
    '+!c6O(mo+ok#PwZl9i6IhSYa+!Xs?(&=CN;1QHRVi06ufNNc?Nq@zhHD__9JKk?=F(!qSV#Hw>ih_fd2>>?zBY9wGPOTFKuEEe8y(yoHJtRHVoDF!FG6LLiE'
    '&p!%lv3n6Y(o*~hMIf+8g1`JI)P;I!A`R+DFfw)&3V;EBFny)ft+^}dT1ooQtQq2ohOy|1LCa;t2K)pN(zg0d|G6>+{$8u8V-djHHfVN3=?!VVRULU5xI&dv'
    '=h{nzs;U6<%7l=mI-&xY%0&w-Od>Mh;K0eX>4TdoG7De{gF*&WfT%N58QPj#n`up@wBFd-k~yj73mpNxRrB>tHQXH(vv(IB4u|R|^$I@`{a`kgwn$&pRiNmB'
    'x+GD<zX<4=lL2v2N$nIcA>JY9-!R6Sws=!uCcmOLDOIE4l22TdgzKS{a-<u@Nz#Ty^!sLI1WJ_3y5RzWZS;iSXlKT}4DA`66~p}W8`V}_Yzm6eunDBI&hP`}'
    '^kziir0Z5Nc7j^Tkw>W%OrfEEee2&i@cgS$Rt8Aj;q!r5DLms-kFq|v1`b#4#+YbAXhetQW=!>BWesx8toor8GWu?Q=kb2BZs)bbbiIik92tTAX4t=PZo~`n'
    '9{z?KzF{Y2mmsI-+EA1<1^gX1RrArcHHq6epD)eGixZsxeuD2JNb^_cqzQ+Wuf-(DsVLtNC7n%1R-BymhL-@TjulH43c#IF%V1pT3}0x%q4z+*+UZ}YlGzMz'
    'PnRq4Sc;TR?n4a72`~#cYkV~@K8mF0?Oe_edQ*y>qow7AwF984g0sIbPCflmSDJAPDKUe^F=&VrpfD`_ZF)vsAa(95W#6B#!)t0G2>Yqyn4E|z>0q4;YKqR!'
    '05F#SZ3FH<V8lrK_@cc2%Baz(w;!7;c+bk)Q~R6hl!7ekZYw!<D_dGv{a(#MTe+{~op6=3T)`+;P_t-7b!Gu`{J;|iWP}ZV<Mw|ZHHjzq(1o*Q>Ji)+d#9d6'
    'RRbgJ5jf0sBg{p5zaj~F<8Xt96Huad4$sHY@F3Ur20Ndv`z0k!S3N-pz+zD*4L745V`sUosSvCv;rLD!Kq}zl1`)ia<is1=tTqJWn{*(ek1e9pOidts4C8wS'
    'kW}X7SqL56HD@?<)=Zy*e`AsF56=IsRPLuM^Y>NxH&*1vYRCu104)6&%=wm$U#j~sREZDbC)zWPZkr#kC~?kBR0{Q*G>Q^G*A2-ukOGvez0VpIX0Zh+kV49D'
    'qa+zv8h(H`nE{qkT?C@lV$cazM#XYmNtjrmEeAj87I&!WDc2%Nd6`RyO3DT0PgGn00~1i+{LyL)6!^t=yPegGwh-U~CEP=D4AB=I>5JMZZ`{361AzLT>j0Fw'
    'AtZ1|7zJ=xZm=x2QYJbZ4tItH0gq>}zh#hrbT)_FLryR&5WtR-#?eLK5;PRpH`^PD1aYKz&VDYAL4<-{gCND>WV?)nmo%WuWdJ&0ah|l`P@GA!-Y*wHC-x7U'
    '%Ny|KW|>S-=0w>e%GE<i!bmxSNBAnc85M!2E7Y4tDOr~oNo5|LOV)p1B)Ji&=j$37g)4E-XI)|TS0<Ae1wKZ#eEOp6_R`z*HM8zXGgWB?MjCPUnQr=3TdE_s'
    'XClh$`Ww$heFv1~##uLYm7tRN)Qd#xr>j({My(vwyS?Zc$5)Y<dmubeayj5Z9YVxcytBaW#aGjfC~-$o(nWNNrr2?~{L6B_5eM<Pa(@*}q@s&`P$8Le*%FL='
    'KVlmm-zBXIB;y+)MPL^b=vdRQ^PweTM=25-UiSDXz2*wbNjU22JceqQHJ3D4h6y3Pz6VwdO0*(H`~q=Yb5D%84Lc!uT6)Jgjb5J$F_**d8vg`cf=!>5h7<x<'
    'l+1<abE7N;M_J`isoJeT7e%Zop5~xnbQ4x7^QgJsL0g6hfkg@Jg&qKP`1s)xqPjv9E<Swl7oGKkpfN7dlH<l;;6E~6e~T8wwl@RCa=os$kXWgH!=wH{<^3zw'
    'Y~NJuNoe6xHfU+#?^x~0D$n+9b(_pRU}k7QWlp!%_>X2mI4=k#A3(k_9n}$K)s;W$3wzMr@2UwZ)?`>>CAq&er62o}THg%GG|d2y3Z0Qfs}q(60AwVve~S)5'
    'U0^BY$hDWC{P{7Kk~=L`^?ajYuTt@{qD3k~&t)3{dM$6%{YX~4p7$tA`rl_;@sDEk>-~7?1ZW__`RVj|zBQ&|@uJc8+WP8qk<5QUb>)E8dWQH7hnf-{SZj=5'
    'JEx?Uv3QYh*Ary<4PPQ51BACC{eo8_{W{-=^b1{vbXFeNs{q;&UP43Rn}yL!l~B&sjDv3~xrmTJH!~i<{1N4()I8!ci&jy|H`+?5;l!?NNNST~SdkDfP%+`+'
    '0lD+_Sq7-l1(*SaXrfs51gLM}-%~@<A&=|&sGsVcC@#K6cNwB*7b!FFTrK+lqJjReNlOG&LGEXo1>KtQkJZb?&0Rka!ATJe?kawv66G?z{x=09;Kl*s)yUO('
    'z&%oSh@kt6>Q%{dxF+v~Z=oNQg2ddbh`GO}_g>{MSpKQPxz^Z^$~<rDpZ^c*5{Xfs05WDBiv7P+)o24ynmbbet?UiHqfNTK8C}0Asj-U^M-pD-5B$3ur)T6#'
    'SOF6VqEu%Cwk3Q&H@}rmO(K&TpP~7!0;tNm+`6+B9{e0{V5ngrH&J7Jb@Jw~raK-0G;%yS)MxCd$pF2W93l@tAtU_p;zS>4#8T*`F|ZX&Nw&JS89pFAIt=hB'
    'YV}X*v(ZRWDG#)AS#{<{A{X4o=p6uxdvTQsA!UCAdn1223Uksq>a&5v{w9Bt+|kSH=!ZSfedaep8TxWV$*yd46Xqm8L%*HxlG)t6lITJf0(s|@<lROc;YI*l'
    'a(G)mdb7Sv&O<!l8&;M3J#S1>=B?kL13I}UeMck&&yeh}UzV3%F`e8UPC|L8hVe+)HA7kS^7*%~X}MIo2#(|<!Exnhc;(NRvD`*o*(7Q(5Pju`OITnES401G'
    '8alV@=+8yv=3P(d;+mZw&FTW6&eSfTYUZcz{g+9ql0t~<bT9hTowUR>nz^2N?q;~~JV_PTY3Fw4I?Z4fo#-gC(SBfEsw4*YuSpC}zr^NjL&`gz`xit8rxqF9'
    'k3~i<-?+(~SVfpc!j2WK1zuiwE*!WS1ylb~>zm);KU7exdWHxO{+4VM=l87k(taJlYkhBFOrf&xh)R{+-YL?FVcZ2r##A>3TfWJ)N?O_$AygfHBS3$?s}YiM'
    'x-Qq(n<o_AcW0C3C&K)U*tw}>B3f^6Cq*vH#-v6E+%h0<p)JL>w3y!rXZ>{=HytMHU!;S2IvVlvPp5;^*xK2sF1P;c3{-9Zz7qc$>iDf|@I6luInCzMFHxA%'
    'JUYpVsH?tJ2TUF9c^Jo&&)i<h%jJ#hWUr@=?xw|K*@)$JvIVzPnX8)cmFE1EUIgp*5rBk<uVTTkVvth`2VlqJK)c_Crf323b4kHkc;Ft8!W^dL=M=t(SQD-~'
    'zsdjuls$SSwSpp5V|W*faBik~1%w%qSyh?<x=xgPPH`oe@TlZsP+`6>=Xenw^MNWALC4`IEU|F%T#e?21>Hqe4IRS!5pcw8PJu;0`v@<7Na_w>-H6k^FoF*Q'
    'h8l=yE}Mg()byj<s%ZJxf_yUIAiqrYXK^k}#E5j7PIVWzHj#pxg|#^n{Lt|CJjoSvDTg<8Jj*MFdX&R(sIleWNz77v;F91P1KqrdZc_G#ITD@iCl9COL*xhl'
    'Bq4%!gCrl&n*XCT#yL?0$Iy&_j_%;=w$#^RTwjRsT?ESh69~!zUVy^89fzN^rHxnl4ybBwX(5$_P_}AB7Jzm%ind@yX%+rE1CQa`k>OoHf=;2y-&O$a^vDko'
    'moUQ}{@p0#S^Ovm-n3S^qQUHPxuJB!847n@o|u5=c;!i4Ef8T>4QD5Gx$L@@AA!`be>u}zspGaI0>})7IzLL;1dHB6Jqcia&FaMBWP*rsQJ8?v=IMb&Z&6dg'
    'UCV@T8R$mj@f>KCMzWjjaL+5SkX3&*t8<OjKMjxS83kv=ao`hdDm0=_{6r$zRV@hm;reVWx^L<?cPUSANzltOS*XZvL%5kuu>AS!0bz`rO&UT!T&jB6)4y5l'
    't~v|;&upc0(fAp}v-<r~_@wN_&Q0MNK4QWH<9NLh;B9i)$il}0Rcj@`o(I-iajL?0NJY?N%5dmy025%7@Z16HYa$Ky?n*ufj2px9d$l1V6?8xw4q5;<uupg%'
    'zOcy#UoW}^uzrm>h5_;bNP{U5IKPy;a(|%{lTa5xQ^u~jyNto-fgW+f2A#!*cbCfL@bKaVz<83iwC1TPylxLB{3JsSA7^H{tLh7NM(`2Ni`Cj;KQoo&qka#%'
    'btljc(tQq`-oI*>wQPaitpEStsj8RP?K)G%YA>pk3(|3ro|UVvb;|$oVj!5fU<!S7{6{PKzdP-BRnKp^j(zKw>C3Mi_<5oa)%9P+k*;qH|K?8nXWbflOu>tL'
    'puW9N+;Y24T<5my?=IQDJVU5|&GldKcIu;pq7NvXtPVch-N^A`=D7_`uLvFo>rnVp$|wJz_Wj0K|J=Wj1PwNU6|;4KWF1cbIR1gxaVxrcGl%+*9TW||msMM;'
    'i|Bsns+<=`Ii0DFLOp7tIF^5aA0psiu0=zlQ++_`Y^&;ssVU9Kw*Vp0r{jEJ*MpVhpeTiOw8W8OIu>=63Wbd(6+UVOsq7NFitV%$wV$!G6J~t&!D+cj7o$;r'
    ';JN?>$MH0>JE28PP0X^Nf?lN*k*-#y#b?6&jTfi*a86XS{<jw*-tZHzeIQI^T5~*8?NrI=KkNG=5<}c}ORiX1IbCwgGRLHqe1U(tw$Ax~q4wb)9H!UobLAY&'
    'P2%VUWF?l<E0*|{AyuxBp4qK_8S1}mcHb)e|Nhb>t?`|NZIxG!l3+pJH}J*ar2P8S4e&&H9KeKUFGQ)_OwtnQM8lK%y1X>WGc@R-5`proUD0hD@MX0mjN8GY'
    'I#QU!*Wkj~B}2`g;LF)*9<)(kQ=*)$fJN4<8lRB*4jl@<3?AN-4`#dp*u&7rFWIJ4m4Ty^KyU`=MWixn_^Olf92#d*c{n`0f!;R^C4lM_hw!8!pvu*jcIVCe'
    ')ovZx`A5ff{`I)roZLdekI>ZUx9g^?Bo)po=Mi<k)fCGkR_~GkIGUnk5ejyKy>6#I|Dv3ezzDK`u9U6rse8>4nj0C%Gv)pRdir{P*R=gx-S_uLd$dAB^{V54'
    '(^psBe)jXq+?#Iu8QQZXG)B~cV<(sIUE!(oeeUwL!I~S1v<F3ygHD27j^u+>b&CT2I8p^oUNgK*pF9w*pn5Q%S+0vk;f=JalYi32mj<ys5jn{>#>p3Sf(0ci'
    'v~KcWjv)MB*v3CRZE$8c)jQu%HXRAHpQX{|WcEJ{{z{TYzpV0XpL`!FML_;hJ*BYW*UUzc<&2a{golHJIF~4ipPz;8ojRdNX#ijfqJ_F?2}N}+Aw<m^hruM!'
    '+O!R9jsm(Wla+hEHYk;4w-OgCt|MQ}w|Nxu4H{Kn{^-6F{a+D3y7wSz1<~bgh&PY1X<n=T46o&a;$;dSAz(lp;HVvbZMy|udNQW8hu9?jE?WaIqDHDJ^Y!2H'
    'etjGmUmC5cfd5-5`}G3-);TArI{yz%ap{HwytyQA?0ertvf*XUz1+a?^2oD1xVS;`KmU#v=^APL3Qm{;ACU09=Vslva$LWL<B_mh<=0cFUd#Eiq0xbD>0K+s'
    'AqIN;E^W(j2rO|9rQgx<3w&S#U5PE{K1hHp&A=AGLZ&Aax?m69Tzzo`Hq>e4PJJsKKA3p!4`53RuUy*#hSY*Vw^EuB|KV#G*Ek!2)gC7ZH1LmAMZMC?ZUEOv'
    '@42}k;rX2=7j)FT8{ltry1H}x`etYOLUoJ<yaMw(y8rm<Q5l}*_R-7Nf#}^ndW|72qxi|y<SI@3uUt`nQEV+wL3;lSgd#t>ex(OG<u6^GjBe|;{G*t|`5N$x'
    'QI%NGjf*67-(2zh?NR9;yrAL-3ykOtQ2oj3$uHIW$yN7y?hn4!6!pe0#rw&+{?U6enBLU^h$tsHJMpZfCY1iqgwEZl=%+vD*T8{Be?I>)1%Lb|5VX^u&Qe2p'
    'S(XY4YJ;Udy;=kF14t)<@_Cf63jtmpEPXjL^a!elbg$-e2MLzMug#Lr-aQkq8)37gh#YwU9yv{z4|DPmZ~}+2Ip@|y1HbOb5p=qrAegx*u7&4czjnLb(-O(?'
    'r!lwsHRdMNFWmDNI;)Mvn;rIp-4b&cQGB6*d?BhwXsmPqGB8_4?|;cA0uY9C_<BjZbZaQZ0<h3PfN~m|lsrt|q4#?Y8cs)GkV>=?5jfi?h9f6}8O{~Z7rq_='
    'o>ehpx;%{nUiffAng3^O=jl&-x@20L7hZSy;0<RSRJb?kmm@FhhRxtJhr;)t3v)14F1s>ZbI>~4>&qS`^uGqp!^~b^qy?_F>pAANu+#DN$|OHs^(dQ|zGd4%'
    '>mi;M?TO<dx%{%*9@ekLmB+Ohn8GFR@epizKJu=9#M<83eeu`NRqHflD7W2{VRpxT^l0q23$c&WAQtjGObedKNBM)?o`(C#Cf@OjM}zUiQ>S%i*qy%20$aN$'
    'Nxm=3FSWv8p8qgr0`*bhGz+=2;qq|3h&jeRe}ry5n5mCpDiY4KOWxF}zZPuWLoIu%w^z2%r=RJ!L(}S^ZOz8Hn30JT2cdQ`^w!Nh81D1D)%<1_W=z)o{*^h|'
    '4&HIU8+(6<8}1t&+osa_h!3~^Qva<`jcyiQZ-JUjXQ#F&S2d-4@vp$iyQJ9ZOE+Ada|y0GOgO~pus(1OJRcvC4{MyyZ0LC-N5?*P-MR^^Y9nME?}}Xg6quaq'
    'iC#SJO-}AlbdC<M)~DoZ@c!m$=G{SVe5ww6?c%f)cdsUe;C^uU@J{=UOwmq7UT59VfZSROn_M@`MMH(du^%*U#y(?zHFSOmhRwVcubsGsw|gI}?%$5flG7KN'
    'Wiv)$_?BHp#oqjLwf1+n15f>Pmz`DYR&v=L7y|aPuYWoeK6``0AZk4xJd;@Mz1z*MTWjIV{#6?RQqDq4Htnv}vqA61Q2VNNL&F>|wricZcWR;OEMxH{w=r&1'
    'Xh%2o7usL2tx4l)EkwjjHanSCjj3)X-FzK|%p=3N8vNvgAN%}r5P5eU2VGCu)e<{pPnxo^*{JXm&#w#dPtNwjrbl$izqVOc#Z2k67uJc-`iWX_j<@hZScaC>'
    '<NYA_F@68=*R%a`lny!uy98iN#`)?ue0-WyALX$B&2Ef`*YUA&915Ct%Y$<i6KwGs$s30S_sZ5ub%Sql|3@KyZ+h(~W5a3jv-NI1)*tGk?O6GENTiu@fO%;5'
    '$Ks$Ox^k^$Db(#p=+ak{{_K2Bf_pQ6pLzFXBjLD_PiCiMw|6cScJ5wyP4*rV(M{L0Eb{5?yyBbz&U<hTeS>Tz9qtEOVKW=6g?JCSX&+|Is58p=+O_-Cy=C%N'
    'jUT9GVR7h)nb-TsBxEhNosCi~To3zCzPGpRA+$YsXZOpZt>f>FB1S4@?}hD!`SQcra~M25;n=lpr^0+0%y@F<PV%L?7}a0W;>nRRxCVRP(C1qbe>BsmJ!C|m'
    'BjgCQO07w+Rn4bZQ{z?0R>rY`y;rP>b{B88F6|o|TmRVRij<B1Vrt1zFFvfAABIUfby$$uM(1nb%kueC-r_0@D0geIFlM)J-J194aMH}U`udSBZ5Doa=+)4w'
    'rK?;^d<gFwne<Yu#2IUG((~lScyqUFObxVYkc^L#)6Ba)({Blur8C#?J7ccFdy~npT8VBc;0#7gT#_4qv>K+m&EP$nj)Ax6ILzgXh4@!(TCU{l-cHK4w>ACK'
    'rg$F+B$j?Lv`@`LLqoXFkil-MmER<%_b>7FaQL>3z4msV^he54G&nkm=DXh?UF25f<i1v*SBKcjlG|_0_SXet-y05{SE_q_aF0v%I1^qU2gfdd8ZhPL))8J7'
    'J&t0aGgx|q7MnFtZWp#zA6L%g9~SHO%w>NOeASe23?`!QD=}XkHfu-oCT8q@6}CZUzFpQcZO<k-S(|3TLE|A|@0i1av0Y3WdtW1W@nMmrdx<(}&RY&tKeO<C'
    'e7H+2^YUO#GwteLh%u(g$C&2R%jTl(ibgV#Mx$BszVY{;-O1sz$5+Jh`f$H+PjX_76*GZVV?7BuUq_DVgFlk4`cJO%)DSfF4P%3=nC&I(6|0#fjh3M0BhYAv'
    'GEK*zZ}s_o=IrDl<7M0{%X-m1#$vpqP5JC$8y7yL`wyAbB%kzc;;H$2Xu4h0-jXYOGUQn%C#lc0bGU!7>^>agy~94R)(s!y;mF=FCCe7)tYLO|=E;zubO@h}'
    '!l2>~xZ=S`##MMZS<NMW`7-o|3zazA9e#*QllZpGc7@WG%w)*sFc<(^;N*MY%q8>3-0Ke3j4!kM&0C1Ex$9zUGj?XX@y$cX<o#M?%HdJI87GB!V&ogP*Tr4M'
    'v+!q1+4;k0XehrlLa(&-U`bJ=<G^`FftY)goV*yy3(@ZX43rsX>Z=)YXQn03d-Z;t3ftQDqtk!%nAmEkGwJn%ixz2TTKBGweZQ+VQ&e;o<znwC?quqGd{W#f'
    '*Ng=tlb7D%P>v+MlU-px2)Rb$hK^gq4~uDRwD2AcZ<X#i7zjoaT*t-M=I^I$p)si~N0t`5_a~O?+&<Uoe;mTpebBwjmHV~vd-z=tJhMdov%<z4jn=ruM)T9j'
    'GGg3pfqKtO9+sc(FLVEu^%m)7Ba?sGSe;Yul;~vF%W#A)hHBeBn@q=@hJZ-hD&im>Jtg|N&)mSnyXIS_nfRpND(``#G22)sjH$+A&>_i0+hOC$R;py#m<m0M'
    'VeILM(Y&)}cSnkcukdh8S<T*uopmFGOmD6Ja*-c*_6N^!78e)I*XDBhVqPp5F6erTWF!5!|G|9V`FnP6Sxye)ui5s#bRYS0uE^5BvHcqE^IV?vO<nPIjqZCs'
    'jjIG-t$DVV*gnn1*Y#%D?y0Tr1FxHAyw&U_4PVySXuGWkHlkNBcx_Hwx{!Ngj1i-|FD6W1>y<TKjC5Dg#>s8WE!w9F9Z7te?D5s%%OXsDJGbw(T!|YqwqiW`'
    'u@6V;<x$fxI4$nqay9DZEtcs9jG?_LSTVfvZ_`7G@zxk)dSo%|QsJ7-md;wlxNT_kzh)f9Rw`UL<?Rz+a$0x^*Q(=ItvpG03fnrne+?{_vjy09BWEJQ8hvqR'
    ')IXS2*HfWB5a**vbN&|TPu!!|s^cSCNIIhH9Jk1miRj#J*>Y?<eHg9h=6lAP+|7EM$(r&Dc6ZvDh_y|<`F!G!*!uB}EpZ=;l+xZUxt+Jg<4Z@#mOb;1g>49<'
    'hpG6rcHU3z<>Q<8eP>=4Ox<LEx)x6_-I4v2DTLfiC!XyEy#BXZ!L`Y!g2~XjTMkv-ubpD8GWz7}Zez+IT0_}!{nQ)O%v-mo;k9#{w~^P~eocFfRHoP|c(_G0'
    'TyFc4FCoWb^SSVI?c*$*jyBTok^Quhjg@Ni>}mQE`)Gt~j?b097>N(5V>sCh71Cp$ua!vkgk2{S-EGSo*PNcQ{&>I?w&o3v<1Fv^d|>k9K}3wE>#v#5weU%X'
    'eS(>syq&7Cx1QbOaUGju)9K5`02}sIOef=XBHu4Jy@}z+s?{)_wq?d^ScYbFZjmq#*4YQkmm!v_j~!9t++%h(<MVnsl`sx6^=2*LGt`zV*J|%E&zqciI~VJN'
    '57#8xE@bwJUa|SwN{>&*Ucb7?wbGSQe_>9tlUlXc=7yX55o7YlW<HliZ1MM@-Wz!eFe@gWNLW*E=FO<%NUyh<y3jR!Mkj2%wAg0Ik7bMrS`#m=Rk64U)rQN0'
    'i?^}y=zT94KQ8%kmHi48OO4vn<BSaby}W2}^~cFh)Z<`RrhVVEx}SKMW}BZ1xy{S6S6&n>2_}^ljJwaBkF6CJc{W>pv-b1b{@hRcOQI*}aXuIZ5%U*4O@s$;'
    'Z$@Wi=ik@goW_EUvh+TS>}K<^c*xv~z)0w<B7y26$VRET!5GMmJY&0<vze=l*GAcM>_$7YH^a%1Fgj+*c`WhK*sYw|G8=eVSx2@=<bJo{>kn_{(wpP;*dlEc'
    'a+6&7tfRrP;pL6_!tNn9{(Q3@f*-A1u6o$HJkwLzGIcYimd%x{o&xcT0jy1xIhq}rrTgK<^=`i3CU%yvq4>p_*Ir*v*tVF!`#4N}PN={##Z}Ekcc_)Lu4%FR'
    'nXvhN!!pp+h5W#mh%MKa-n2`1qZ^N{{911BdbzR4_l3}*zl-+j&hFbJXbPlkCgU;JTI`v9hVItpF7m@@islThhom!e%-G{q`{!t2iU$pG0~K1hxVI!-?!D(L'
    'o<q+-f91#Tg41+z*hrJF9GhodtK$6CR5bP7@98%m8GUdV`Ha^X{Im=rbHCR=biU^e)f6q{%xwJBc};DnbU+v+O4iqiuoW#|IVx?Alvx+YO`F5j$JTzxvSd0I'
    'Gm@llWO#`=Kiv-tHg}9QYc7FJ@1s?x-4HaMf|Wp|8;+DsT&^{KbFlVy_c*az1GQtn{TX{dt@FX9JvN^oQiW>lleD~MKldxwy}kZmN$xg<V!|bcXU_d%2~?2#'
    '%hCUAxVwDJ-hZ%INke|?Sa`mMiPHyHh_?dP8u>NjjQ8PSD>|aGN8m(JFU$6El1;kIJzpX{95VgFDl(cd^+G?;wKRkMl6zKRqI|;CbCyIf`=G`87M}WRrL+}{'
    'a&I?I{p)(s@n%i!P2&A@Wu@*5B<l%f2M;3$pBZgKuEf0EZ3hQrndD}P=4yUua&~5BAuGmxaXJ}sBcDMGHq5h`k=^Hel}UBxu-cCG%6$3uW`1i^Z?U*>bSSo0'
    'lcUpBk0-r+$^E)*hZuKp&%Q3)?ztztsF+R}`zT%+eN=|4de_vc(&=8?{7D~^u6rgv=2C%xb?0&H6ZNUT=dF7_ydG!S8+|Cby77vmz7N#BFDAN2KP>Wg^P)mF'
    'y02SHQefiiO)S{v217A2&sDY-D)l+E4DJWLTC;0?>9$^yrRM%%ZZA)>hqnjwG*t7}dS)S+@G;|ZFC3mf*vY=F#$~zefPU#&=iB%+{c$Y#c-GRn@0;#R(d|bn'
    'xo}ork42LoI2j)q<8m|Y)Dz{EpAC|x=G)en_;5LP{%Rr+tSkeW(P!0Y$OJ+@N7do@0EX6SFdHVkm4|TGkT1{dr@{XI<f^jC@xb76`OKez(nF6gBtE%X?JZjf'
    '^h&e-{q`;LmFiTu&(A!$Ht+KT7sW)obGB_O%}7%v!+0W=J-vL`=bLpy;N4q`w7vU~{oQy94~rR}r{C#BR+-@XB^IMMFaDvuwp_0!AB)@rcmE<L8|mH$6&)2m'
    '((nCd+`e&jzt~0pK2%&azjn-n-?NJsKUd4eD^U3^CzWqB*R95!z4wyFz~s#_&a6_Nue$Y~87}?tBHMV0oMQcjYgmn#2MvCaHMw3Z33e9lH)i?HCLeV49phsm'
    '6b+ohwQb}fF^H_3CQsNI;_HS+r)-E@?UcA}bET|f<+i;RE1T{IT_wkZdTLZ-N~R&heYTi>q_ZAnYA=;sq*!b8ZC?*oKiE)yw)j?|eY;ny#pg22JTn{3hK~Ho'
    'X14{pREbJ?jS;@<$#C3?FC8jul6<h5*E?%#J`+>B4)EO=^KzW&&gisr5X+w!*SNc{3uQx*qS)~Kr3);mSypJ=w>~r7)7X>ZtafrgNHC?uejE0O`OKiPIt-G)'
    'pg4&8b^91<QR29fbQ&@ak@<KS7%cwm{+;`Ht!*kz*UH1zQ}4!zII~U0ll77}2fxe~>p^%CecSB5<VZh^sQjqJrTBGkF51Yd7>haWrkpEaH${R~u3G3!26<C('
    'nFRJ~@xzf>l*3KuVO`0QjY_o`DhD~Q-@F`E%#-ZBt8Mg)f$}Q$<qUCg|9v{%qP#0Qm^W-UZo61^?#i9aKv+a$Y;8R>OopAw=X_Of?Kj!e{infVTGn^o%Imv{'
    'e`i`wU&Za_9n0X0iw?gWt<h3$Sa!eW{ME?&d$mW`?77dn)6&0RnY!C_$uWugQ}3lr>u3ntzpQqC&E`d5MYp*c&Aqevc_Tb%IPCms6yf;FxE%h>yqQX_6uq}M'
    '^4)o{5wwSk7CXCWHVZLl-Xt!UlZm$y&l{bl;JeXgpcaYj>-rR>jK+6+JCl2J1-zWF9QF;ap0#N5CPKTU*byd;b#^#+wSs|ZmmEjuUz6b`Fl<j<sd;divn5aL'
    'LwA}mq&K@tp}*?A+<#00m6l}|Xt1lTrxQCBc4dl6tc`a1lsR&}oq3qbr!3<{iq5@FKdO#*YiI0AHEeW`oE2Y9ZU@(z3^JKn-jydy%SbKfa2Zn$ezZMx94&Y5'
    'KJ+%3`S|zXE^Ko&$s^^pczjJ?VJ{{QuFfth__GEtpQx>0Z8OTW$=4j)*rN9pwHm^`Mrzn?0z=wTh+C%J2VczG7`#ke6Cc9_zP=t9*Wpkpg}2=2>pWgy$OljI'
    'lrm*Yqu0Y&Or?#p``qiY;rGnj8NOfQ#+GC(ll?T24_<pE7)$%#&EaCL({WXeZpZ4_Jq)KOAXFNOh2a5g|D3rp3l2Nw_~|X2bjDi`Z@x*MoaKC^kxW0Bw?TGB'
    'y^LD6a(~!q2V!YAnU9*h^w{WkcMOhQCwT0C0Ey8yh~-(^SGV!ARk*bjL(@Ee>abMBRQ)^!93@kj1iLi%<=_hw(NAycuZH47fb{I{8-Tb>B*%UB0^6OFwmcZ^'
    '&G^<>CC#Q+C!5+f!Y*go%?^&QRd>5t^KI+9btFBnMrYo4dnTQ64kxc6%X@j8uu<<q)z%+19bc_C);thQwv(qZaEiNTtuWl0)3&}n6uIy9R;|NeaoW}snf$)H'
    'ZCYaOiQCup7WQM;xRQ2PmgRznEJqpJvRVoq>PK_l*_-o*y2V<ayxZ%ifGs;68*K5CI3BhAiEwdWTDniRms230ihmlGxk2ZxK!)>XN2=YiFJ~31VU5=4ddSoB'
    'zgkaBd=N{#nQBI7BE%LJm4%74Q|)7SfBKq_r`7I+6jtVu)9oF$W4tB4<y%ST*Ekf;)&jwI>irPdxEGmjv9un%ZQTW~yXl&((?G_y-!inVXgY=>p13gl810Y8'
    'uf}1%JWV!Jo6zd_*9mHv_LqvbjF<0@bBSrN^vb=t>u>M={g?BzJn|2X<#xDSH8HvU#uYho6=!L)2mjEWfuCAW<HO~2P5SL7^MsGj;wdq^wtDj+7PvwO<Hl-V'
    'EgY?VKD?%?)>pQ<|Jv0XkzCv9@<oryeDggU<X@)4j$!R9#&gkJBl=!BkXwH)UYMl}jeRlL?OD91`+e^IR5v{|7@Ot6O4`E7#{1TJ3Rp|Qw}!=Ejb~EjN{-1`'
    ';(^S(Ye{+cYilhsIh2~EZe}|@t-n^0U29PenOFUtJ8T19`Z)jPNvCs*@%vG{kGzk)4QGR#h3k{NIb|wZde!1rKWl%T^WOKM0a&3Grf)g4-@GsUAZ2weDJHSD'
    '+v(zayjL;W8<Z>anMqaOUxdD;Ieo1kCizUxTfH|`Otr<{_u9zYqOtUS=fh|pzkS3f+x^R)Hy%2lv^cMY>0-*)8e0#c7iZk`@#%_86PcPf&>hhAShD*1*$p{s'
    '{SSj}R}fZ*h3k;&u%mFv{6J^!n*s7I$B)0(bNAB1=3gD{b@g;g_c8<j@xkxx?zWsTI3@GB&SxoheD!TbzrAWGk0O@0<G5)baqD=l*rnP|s>cR=o>ptoti_MM'
    '({dE*Jgg4e6*FjMhKJ~=;&D5hZy{HPz0de<^hZVL3Z_;6uwoD4FUOa-<p<4TFTvdlF;_e$uKVuUgKb`TeX#Nk3njcWEVY}v8WHE%^<px99ABrgPx>X%c#V7N'
    '2BXDxoKGHB%e1c(FgZ+o(%`RdONCtbvnGVZ`j&rv4a|EFukWStz{(9*g)iD^jaHYLw`g|g@pzVldfVH4c`MY%dAj_XUz$griEU=j0aM!kcK@;}*xyf?6c=ka'
    '_K|tEcW}+$qOO(EPBnRh;PQ&|(cU&6+YaFj-zYb>i|t31j!uv6X~_R^pijrKE41o}sm*$DOgU5D>dMnD0-rEC6ldLSY)6G7%zA%cC`AqXkiduUJMRm}F+x(a'
    '?5UfpW;2G|to!nLYNt&VLqC<MnUlp{n5p+jK2;TLabr0?t;IfaQUA*8<%JQwpMRL_`;qgWwKZ1ue!x(TxBypI2ZpKR{yy3&ZG)kL>BBBk?@PA*@Dce4R>va)'
    'zY5qg!6=h+d^(1f*giTtc&d#ClQwMV?#$s52FvVc!?QZs_f0bQRX>`Xy<<0L{~XgoXUv#Zq2mji5I^lqYeM$ehhZ*L?7UW@j5T469rCsOJZoSEJimGH@Cj=K'
    'SW_=Avmxa>xqF58d+}h-`+fY<YntwMtJr(~-593#+q@;6%`QV!-chwo>>0*;pV{Q*t&KT%iZ0W|d}3xRX2;Apel&hAj`xmsXkFcIOG{(xu-^L;{h~c}U+%hg'
    'uKmy&X(bXHVVudiR$H4mf9P91=2D36?>AqwQRY5-`eLVVuGq30I~@Fc)+20p*3fqPP@K^n(?)0|lFPkwwp)Gd{Rxw!muPYae?2rGwwe^rx$>LIxVLn6ysmPk'
    '7tU0i8MkS@t#A9B|73~RttDSMJaoNS4C8z;HQ|zNTOsn6cJgnnZJ@;6e}v6uF=UF({NylP9nJW~Y-VY@Tn}8q<Nt^(;$IzMe9wCx#D4Q+v?S>IOMaev+q>r6'
    '{kS&+_Um-w%4hZwjxD-MLp~gySy!1H|KhkOcOTADuy2WleFoF3>ClXu$h67zRvEu8W0j%L%_b~1?`+&~9bBX-TC6;DbCqG+R-=|JTgX+}944>Sf@wz#rb;UA'
    'p$(b)2H&mK?DeFXY({F0;nZxjnchR8ZDyG=&%E(kX21@r8?I44=66favXF2Dc%QQ!=!%u9@2fc2xtRFAP&c$+f<3>770vx|KhAa@__3i=s@;pW<CHe`JJD^v'
    'f6PSOoPAwS%>&+icVBp22MR`hIa_sB$NN#;J!&mKcR>?5Ed`6OvF82DYu;@zct3p=mX1}*u9>$~@Yd_&ukK{*tT67AKUOlao?Z^{wDa?|8UCVPz5Fa#_3`%|'
    '!zBEAjQ3ogt=VaAycQW#rEFi9yKQsX-26&@IR*uf)e|*@yaLnjGf5^G9?!(kGLsrPBJ-NF(RL>qX)0DP9QTvrrjZ`Da$rLrOD*4P^(*I|QrY;2$!GOXJp5GX'
    'yZ~ooZ(Fg|?brN;%n3m;+vna_=0hYCB@M61WG9x(I?4l^eYA9UE${ZKl_8tHs;|i(rj|(1S8nbCBWGm!Uf7o1z1>6V*cSTsdux-c#GH+KeCyq|$ESK~8X2z3'
    'jnyJm=4a-qy+l{vQq?LS-n@4LQ_<}8_?X^=t&+vqda`OWeq(I;-nLQhjolG9+4=zQWuNl%)|t>fwy4C+-QRsA9O*#HmkKh`x!uIpT0J2W>XrJ9yw`TLXFpv`'
    ')D)`<VWXHErwehqXeu>YIqu{w1OgQAHgu{{E)od0_fhv(x7SNf`EoxHjwLLH<}^F>uJT`2A6pm<cZSlcEPRfPLwkGf$pjnzmo&fWW|?Ht`+q1n*QMp4Fbp3{'
    'BSsoCZ6ro1loBG@q#q@fHbf|)&9Q&)cLI%B)^p$2wa{BVDRsYyT8+p0Hp*v1>9F0xSRUdVg4XZJL>(%p?;H2#L?DeGdSx}g)V7TH{zOroQsq^}=u%O4c-h1Z'
    '5wEr{@bo)8Z_u&bmdJ1YCuCY&>i6+LY#6i#Qm_{F{EFYF{;(!$O)zfPe~p>Out(RDM&-r7U#(`R+8gAxeb9`@Z8nFGOg~-7x+f;HE{3d?dKV`e)Xa11txnN?'
    'JO-$3-mxpCP+}jYY29FF&Q_=<mbNW+La=l8$LZ!l3dYl~YHKbTJI)IOv`0OzsRWj^^afUOL?}Hyt?qEWbgptA`5vH`q-g#n7j4ELhwEmlZY+<e|2DmK`K-)u'
    'M98;}D5V_xt?Hd1m5dvH$xSRJz(E|Lk^4gXIm=;(L%)@t4AH9o*zKb?@`<@Sw$GY#^F-^Z*FqiWOmEMqH{g2;;!kH!^BjMYT52`V`e1j~g<Sl9YQ6oW!(){b'
    'AH<>cx3KcbTVPMmd5sIvz`1PIaoV6MBIy1&udC^53DG0rpxc*WE&kTQ<@&zJ(f$Kzk9*uE7{c5Dj(UurHiOC+8Sws!=KMB2GG<6KVa=v#buV<4T#q<*A@G+^'
    '%gj1w!fPEK``O>-FqquaR&3UcyR|#_w4f6;_gR5^b`Ek7hCus>RnIzdsan_BhM$t}5gZ+AU>yObwQZ<OKhPvg>e9RW;eQ%f^ESf7UoW)^Kd7)6Do2W^YSt#1'
    'L+8V{>N8Z{<JY?f`L}qJ)_33`;4i=xxB|M>EZCkFrcQME?PfpC(P@9N9Tn<HYuqezu!naJc>LqnXAe8C-Z$;aK)8RbAB9$Bg-lw*Yh*kg(qBg$&bm=`4?ptK'
    'fxkUjjR2oH1=mFF6XO5_?zQkE2NM=26JX?jM{bY(t$C(}LPgj5&iJ?~BjUOy@n0gbtAZ0J<Ief<McPJX?mt!)f6{-wSLF15ANTdicQ^pn6Gq-9`P9Ibwo`-J'
    'D!-@Jf9C6Ul7eh5egMc>JT@M^^Q_^Z{(h`Qd85UKdvwjuJ|zD7++XJaB2D2o5+00KPO6gJq&vwxLYo?Wo%q~i#67|*{MknPC2pjg+IqIPn%ijZ>cDyp>^s>s'
    '!YZ>}T+g3RwFh5L{GgS9{8bGoe7U2vlDkg$h|1oTxT(6pTJ0`X!NTXxNe|r9b^KGuhrCKU16`gF-5F+82h*e;!7b4}{mIv~DcWl;njJn9qeF*iasF{M0Lt1Y'
    '_{LAMkO@ZsS$J7YF2na+3v^3TrC|W~o>cIh)f;G4NG44j8`R#vnblUwd!kRXE3+<mt-U7aGoT1GUzOMH=^XW}K2i}sKy_pE$l{3Mk+)ky?sN)M!DVXyI3BlF'
    '(V=-s!ZC}{1Yex3X1N&!WeA*n9{j7L`Qwj=>YbVK%<`Fqz@gDcv|LzNn_#nCzIyxhpeqjL4FVf8{YFaW9aoJ%=H;D$9V6wri^l7xEQpmxJPHUus&$rr9yRJG'
    'tY_AXGyrG`Pua;7Q(}D?!U0UK&db$l0vo-L{bI71ns2G=(0HuQdZ%-Ln5|9c@F>YP^iv-uTGD5#0CRi*?Q{JyC8#=w04469YMaFkchCWg`{m`W${xMB3)-|0'
    'BjxhDa@6L~R6;`U;x)t?gt~1g$Ie*T%{HC6%B}eJvsc%g?dhgH0|MklwP{D6v?{)YH5tcUc^>wjmF8HYSKE9(DCcpC*{2w2&dy4*FfW6?MiaBJj0lEX6t#6g'
    '*64A``ym1D{Qo^%_XmItY&+ZyBiOVGziOk~ikn_h>r^}sxECxd!);T_;zf+H^B&cyZu~iIqPXGf>eYIUg4U?lB;mC69V_5l$wYaXL<E5z#zsD4pHzi*NBU*W'
    '+w$PFU=`)ke(I`8)GWN3wSu?+M~`OxI5aBQc=>YRZL3w?UM@!0ljgMzUb(ER-sR$rqZ>rdyf-!C_e3`v_-`cJht431#Ae`+p{%v_$Vt%*(Z=a9TqA7U%*TGv'
    'VAo>*HS=?|kx;)Gv3c1WjmiI9lm{y<c-f;T3LHNZ<#R`Na_2m)Eq;BYU|b8iy*{klGx%-{1gLOYwwv~>e6^_y4Gl|IhfaYs886W%(#Q4mZR6H*s1YsY&pxm$'
    'Tq+4d^MqGLZSkwtpW93#)WczZ&|Y5c0Gx#Rm%xVc(%W5DkEp*KGaKRNwwm91cSgQ$Sq*5pXV@yKt$PE^P^1M)>$?d{b0g2BOIKcdNjnh7+wtRL#jhFqO$^(N'
    'D0;iB4DRjP7Do-^wP$)#y*`k`MJ?YEEjxHy8l#coW;S8NRZsYBU9>lLFVh&6=^x3L`jk}nQ9NevyxTuu^TwgKnf_`6xmGJ_mMS09+8=^jax00-fIG#<e1@@>'
    'wR%F8VfuEMpb1%XnH~prDNbMrYrZ>tdGD@c*6Twx+B+T$(@mOtCS(pN1l<DdO=$dUB63L0eb@512>9!_JJ5R%bpBKq*TtIiXU3j1R!|}^Zf|1Enu`|u*4oZl'
    '#s5$^su#>te9yV|6v=SrFUz?JUmB?Y$L-6zqW^rNVSBT5d7?1A4(?yio!+dh;aP3+nmGe_#6r(@oraMay7Vm~W%#$ek)dk<^_&Sp2i@}%sAliuDpI*??N@P4'
    'k6TtJcgW+a)8_^h<bJDRyY<arx>I8jQD6$iZpVz<K+E&(TfZxU^4O+#Rz+gq&JlhITzUa`Jm1t~e<HVAU?-W*<=(4>F6H}Y`Q|3e_ZM0W2d2IB?(A9<rr$$#'
    'L3C!SZb;DfGTWz*W|dxkDvHOl=6m`${_Je%t)+D_KMlW}5?ClsfZFjLD=UF7kNv+U_Cb((({oqCm)f^TH)RUDhsFd^<0lS7I(ji?N%t*8HGI5HR^#0Y><y7x'
    '{n|?E)$x270!?XPg8cR`3<BHi)NK9}9yZgJL^vzOGV9n+-?``#hPCf#9WPG^;O5{y+@=^WnbP;%|4l3BM~$10z(%L(QMY651f;QTKlTN=Gj<wsURQUUQHUD-'
    'WFq?Y3~y)G;dB25J$zzdMDn%}r5_1;_}o=b?L~`P@6Y?I*1kN>c>8X{J>K9ek>(AE6rOm`#dLe!CB89<wv7$lDwDBzI!#9sdMI10YR?dB+T~}?r&D<x7$&$s'
    '5P3g(<UM9u>)tMjo?rFXs`DKnx1u2AMwP^|&<Gz_riKUO%K#SsNNeb4?-W(w&R4B0CtG&y5(G1DEyN}RR=Yh*xz95KT4dX5wk<oJ&CGR%D0$cvKI9aA-1Cal'
    'I3tbWs$addF}Rz8BoLuD^u%aqa$fmenOwutx)u$d(e+MN090x?{XVB1k<0zQUnSjfa71U|2FtUea6g+1SgihX#XnNSYJpTgk0FT^7vk2Pe)zPv5T5gOmEEsu'
    '>3BVGn|Xg^tQn5m!uOsgQv8H=!<llgwFd78v-=Eueb=f9FB0w9L@&AtTRUBh_#FPj-DveV_Ult)E}$!Z&kHtZHoPMiwpPF!exT~x8?|>sU{pU&wY4=-{%UE~'
    'd0_jA(#XpX#Z<$lTCJkm6c*bX!)vc3aDfvw^k%O=!o+;Px$s0u+0m@`9JiSrT2DlpN(!D4&sQ_8JlwX-PHJvHy?vT6Z0x$^V`ew~>#KF16Sq$2*)8(IrP^b5'
    'UYQ?Z^oc9q^-f{+$65zJzHiC5%Cel_hR`#$is;?)s<l}3v2HG9!&}!;Fn|la7eGJF4`cSHB*&p6S?vp;<3RpuY>({us9{ixAGV}go$OFs(AV)?gyT%A4Mx;{'
    'c2ooqJYiK((~5aqnu#aZ)(*D5E&2QS{W@=UiWaArUg&NS?&r1tM&hBjQTceIf5`gI$mN1++*Ge`7xOln`^_JXFh5%-_Wp+RrsLbl#9s=xer?e8o?p!1Z(zjk'
    'YCx^BhqSKWpA)S%Ty09vSuz@*O1zz%uVUSjsux+Ow%=x=+R1d(cy((nty>%FSFcj536_4#>qI7vx?jBU&i&=uy!eK6ifb=wp2}L196MKI%VE3wFcbP$4p?%J'
    '*6wznG;IRmmrVKlb;b8L=7GVx=ffA}i?=$P$NpY59cE5E(dRWH_JF}5;_G<lT1)NX!gA3-z72DNm!Iz9R+-c!Xb3@#j&{FNSL<xo3%_FOtEic#r}sfcjmHn}'
    '7az73%kRr*H%g-t;!(%y=64BV`2O?l&YD0{AQK7>*LeaB#D1e#jy^wOJPpe=Ki;m&-?s86(5Kg|RtU{rP?4!GrS5NfzbmwpNIA*f-7Hm)R2cphQD^6Jv8CwM'
    'CLkJCp8L+|Wk@{?SKXmpCirpLaYRDh%Eu4-he%TvJnZ;>XRiw``wXXMqW|T{_`}Wb5h2$g;lj0{NwSiV<9EdrqZ;+0jxYoOfU>@Npm7p5(RDOasfK{euUDSV'
    '>$jKQX7-=28X5hy)6QS;ZogQs=JWi?XY>jh&k5b_ZPbtJGY+<CBs9nKzQFNzl`%#^)c2P4^$X+R>i#sRMtUGm>+?S|tw-FcalOqN4BiU-(W3V*{wzdM`T31k'
    'TSFT`zQB{iiysfRh};_5;@wg!diwg!y*6+UYJewvy1Qa--0N;2-fZB4whrasc{zKh3_WmqX<_wY3yLIY`SEnUYbD7x+|*9t|E~uIs%O2+HuF(VRcFbW<n}R0'
    'DF<@==e_~1CyV3_t?ockLG2cA-;!do*E0`78durur=t|<xfRf(<zmGQ4?wI&ne<(<zhG1rjp7u^6g1kJZx`cR&E<X3+>1?chK;U<TkC(X%9Od43Ag_(JV+3P'
    '4rjb3)Vi-t;59ax!Hum4sa^w29b$E%#!kIQZk2Zs4?yMM*8J!@^K^PP8lS_HVBl31nl@s~JTzWxyk30@SD8e+&N%taR_lf_Ww_ZNnW!qWZ}#o)@7*8SL5HID'
    '4Mq7If}omODAn5Db~>_W#uwLee;4@;`p#n))>Ar5q~kYAyrm^f{*1S^eY8lk33vqix7a)G{(YGfCe9DWT=o`n%P%@765dX-%|Y%R6-1za>-RpqTayZS*v?kO'
    'B57{kg0!~-qapG83yX}VqpOOpUc?p_yzX(XqKo+<e^DH>C%{ophHCTO?fithR-@kR?VVtg6Hj5a$>h?eb7X#-EBC5$&~HDn-3_2`Z~y<FcHTyCow(MOPcQD`'
    '`Dd9Kl;}~Ji{IEYDYw?^9@N);pOur!7F?num~UAsHr{UEgErSPCOwc~<#|p5zaauF%By~UrYbg(_9p{!JCpd-Sd+oV?GN&Y@)fa}a$X4RINGxh((gp4`TjwT'
    '*EOOd?0h12GcD`1`$E?GNl^|nI6fE5Qp1IbCiG36x&&C5p4#;kvof#yQWDUJDJ~`v@>Hf^$=~0~pG19|pPRNFdTu>~b4x8q2`*<3`2K$FZz^$)6Hl8mLmj^0'
    '2{4`S7_(DNCY+X0oA8$ZDQ^XP*U0PPFitOGbJrcDvlRKVKq@?I=+RvM(r_!~OaF@BBszbk%ZR=ix20^~M$xUGk>FSygP*?}-AQ}OPrv~TfQDdRUoe-o0I*l('
    '?0=-T%GZ!-;MUb;xpjKgU66S@B81sD_K<p$E7Xa<oVB{{jW>}Xtz<kI9B1N|*MUXB(h}W>9}r9>`|amyUHUuw)3=Zpx~JdE=WFT(s$CSzPBvo|A$-lwX=S}-'
    'cKxa^YK!{M%gi;X(l~*Rp6+*vdRIlm?HTo*t(#H>GZHUqnw2w?Q0WYI>lS}%8{tc-0M?(<*N(s*SeXA$(yq(heYuO7dYN2R)6Y;!<C-8DiIeYT_9BkVc6w79'
    '>wytO_ZD!i+)t;RI9L6u6yo(}VWnm8qVwuFeIm<htL&smi+kQif`L)f-t9-}-JST-19msB5RclAcaf#_d~~H~m4lkS*#g$XS{@xUbJol#HcH~#aFL_CL+0ON'
    'zJm0P#KVu9C9H2}bGTgYau^zazqjfdz_s&zv`Lb)|Cg*AuD>rnlEa;Oq_-QQGkm_r&gHo4?aBUznf>0)e&m7v+4Rnv-t|Ka8j!On7Jebz-+70;G(o|2ZszCi'
    '^T^`K)L-2+8Sfj{#!Uz}ohk!@GdtAVT*K4kX13Qo-E^+)Wba%FrYOIg;PG)Sekq60p!IvxXjtNeIXYk!DghJ_Us>6Mv3Aqm=zf(ZrT@TIZ;kxhfes75kMBiX'
    ')pK-K&)srsV0vql$mIQvNXiBgspGS8;=`@ev?o212l{X7x6e*-!L?y$10@*U+39p~!=m1Xwq5JomS#^T>2!$-jCL6t9&eG`k9DQ6{WoAkO4-N}B6qsXg`d~Y'
    'lLD>~RkgYKsX=0rReQA99T!r5Tp}4TH3yTo^X89}Nes8f^p}>K6?g`3kk70CN(r_<ADGy>{d+dSI&s+QLnsc6>~Ct`iw#oD8+G2q)V4*$qxgFqmiP@p@4+>y'
    'NKR|HX>LM+SB&mU2+6)PJ_wtaTs%=Ryy5>79|~NTGmW~<4zC;aQ4PlSpsQ=Gst7$yVLw_<>Q%J02de2A$p&*SYPYhFSjhH0kjHOnve<OoD}0PyYo5ClIe&HQ'
    '<0lJj)|Qb7GupEh)9*QD1TE@4Z^NZ#=(^u?qj$rX!R^ExTJ=#vUC+(;iYVw$^+h^Sc;@Q0g^avsOCq>#Y=|?ITJ2i8_OA8ZEXG9iVGrI%Vn-KPJ`bu4z(pS_'
    'Q4!h&YC96|Egaxll!;7@gndq~F3*Ws`sw=z9#?za=Ck5p%uXDU89>8qFNh7<U#yA`d|czvmOglWg$#*WR_kvlEj@U(MZ3$~-<}`=?slM-g-$lLm$d$INP}n>'
    'L)&_B0*{ZtSmqK!dmaNjd07j=sId=YRbO$bVJag0Ij+{3*yQwTe3ju#G*-6cecj!-t0^6KQ$3{1Scz6i5#$$Qo~JwR%f0l`Cz(+C89;VZ_;R+u(ycd_W=)W~'
    'TWQ?wo+Kh_f~-Cp_3yvC{1AL((ty?M`6XgWEnnL$8U<kInkAHHPRu{NB<uWST)aAjL{D*Rt_sBWjuD-cehKG?$6EN-ZVumU1|LN5AA=h6BJ;-stBz`;T65XC'
    'UTOuR%<mSnSMz6`zwA1UxFgA)@d7r`xzm;(>I(?>*zB!8-y8LEv2VSq>(HPUUOwNfBF<|McRJZY8S49sL3*fZLX^+EY~BF_ZZ9v$W&72>Y%;jxhwniHo4YT3'
    '*AI=`Kwoal(UyxLVZ7LR$n4{lLYJxawj$KBCB^xSi%R=A7t@li#y%^*2O)7KhlcH6iEw^iG@&mH?a>x^u~Lcnz9_~P(DkqnbTic$;Hm||kvW;)E|9v~9SV$Y'
    '%)2kE1$2gWrGp&xHt7NKsfA%tZZ9d#BnHvKxlG1=+dnfw%)F+mwvQL-;S@WablMSSzoQ)By;%Vahf}HBuaG0DE^@n5V>RQv$E4B7l)2p^rnF!K4YH24Lci6L'
    'w!#he@15hWcH-YHU9wIN_8|v}e6v>QzVaJkQ}em6p3#OVpGkeu^v?8idX6_YL|xEqi#?f!Qk?+i<2B!G6$cj@<oYBE(H{N2Fhk&I@aGR$+^xD&!)SCS_n3D0'
    'D3_$USAG^<sXvf;<|<Z+dKISH%C|jh?xvbjbb>Sf=a2LDpRvsW*)@$yX%s2mjVieLB&%+(E6rcG`CCfc?OSvD<cwp;S+BZL|71FWtjit>FumbikZ$R52{8w)'
    'n+A>0X!jZzQ9+W~5^X%uGGCK^tCS!j+Z1S}D0bn~ylbCgaId)2`04Gt;0y6F1D4svVJUp>T4Z1C)AW2D$20o0l1AmG8bPmvBoEK0qIF%;_E1w5_s=ix#=a#K'
    'JU12x#|kHKeUX3K0<h$Jljn1DO%4jT32o)3+|O#QKbmOU9@1Qx1OO$ucdx#H99+?We~2@A3kf^*r|VW|UjO<+ZOWU+rPd<#`TDWcmGKz?8vc6q<e>b0i>k=!'
    '`5AQUT2AI(JibbXYM{dQd~K6kR9c7-xcHjT`m)^*+#@Lz6UtYf>^rPtq_nJeho^aJMUMCuyIga!f+~1-GkXbR>xAALVGq2!-6PrSS+ni)zSxedf<S#$=ZVxO'
    'xt5(Eh9#uC1)fWCH>6kz7S7qo7ju*An6LWx)=>P6(wUh8+^zXqtnJ|!(fd=|{(AWfE2oP1;0WkFNMY6J9uHmbd2!O^3(uTKI=C+H0dar(y;F-h?K=@ZV%zG('
    'T=pvSucx&myVhyrH-}@-cK9_{pW0ym%DDx;pB<%Rd3vt3bARX>6|S-PVEz{Tkxh2vkS`UCyEV2tC-%NMzGnB@-L<K@jb>2&GkW#&IT1eOkV&3_^%^~t>yBz`'
    'm#*f3#TA{)?M3HSq)*yClvU^sDsfv&vk_caHOh%YdEPJ2j8ZC_arjp))Z$MHxTgcK6yrJ$jyri7CfA7mtu}*;i_Z-90X(ZW()DusWcItwJ=cEtgBwKLTOszB'
    '2%#8l#9k|IO!?XudQV4&zQMn4cIIr<Iiztl6WKCZCATFYXlQU4dL!}qV2|>MIvw+$m>bgdn6P1aTf58v+6n#k;$)bol><r#<%HrA9gP>qhCQpVAZ+oF8FVbO'
    'PG{healiBYVjZT|#rWta<r%)(EA3(1`^*vD>ks;^v?yxKYU`|Y;j^p;{g@=GHFwbrvH2%_ZsTXH41ayEd7EGQ!N6Lie%_VrR%1ou2jD(Vij=+cdkqd~X}iPi'
    'I#V5RmFU-eg7Y)K=(OznIffcFY-aQqx6Vgx#_*+a)%-b1y_{!rH@h(QrJ_m3FuVPYk6eMhS;*r$IBP?h1bXMe$*H^F8RwUc%cwmzTcLw>$ey+KmColmzK~s~'
    '2)12X9@C6}Y#gMZ+CiVc;`UzfBXGL_E-ZTHYmGLNA|1YsYWxOVwYg2>Y{?(7pVSlPN#hSNuPphAweC`R<1ltEv#~7<MjlPJ1~p`x9=WJ8yV%#cgBe}9#ka-V'
    'W`)M#`h;g7RN!l<Lg)NwU4^XsPFjzN*>NjWqsh-i^Z?{XIocsIu)4oI)!`XWoYO_5@#V<ab)6wQkE>YxYK2HXDpF-HzdvApk2<o<IN529PktJDnaVtV=w#K?'
    'ALKaW2SSuTaBKAL+_{(C`jyz3Ie3Trq+ziE(uWhk*m^2P>)uFQ?|(nv2OkRPT;HW}1MKUewp#Rnk;O*9<thv>r_N!%Et;#7MD`7>Z2`?~clX}5=Ki!?+Os$o'
    '2W5@a3oZ?2r+MX49!tS(+?VcM@!#twi#qsFBR(KV3fukmblDHROgStxP}l`squ8}Sf3aRzVyr&1Z!b~ayjWi-$aD8<B1Dxu6^G;N^m7gaqIZc`rvlrxMppLg'
    'OipzS#T3R^jR@(P<d?WjuJcm|4z$T;FKESe&@5`rQ9P$1R1X38h8s_YJ-p;9IOf)F7R%8gy3WTxpngEBuZ?-W6kA%tePkicIxqXEiH8R-$|pFbYax&)#IhEw'
    '_h#Rgco$Xb$?ib)uan(22CzrR&1ws2ZT7K&mcXbB$@Dd>N8P#~AHRp8<*zF(=4DLIzht<p!SB%zD_(=MzOQ%26qkSNy`N|dhna8PSm%!9C$l=OY{>z(q)yU)'
    'yC_s%-wt<T39^H^K;14Q9z-j0bYb$aixE@JSRC^qk&ml~`{1?Tt*U3*d<e%I2~md^AM)H`9NgMU*jzN3&85=-sNn(`Rk>l)k7=QLkJ|cgRb8=S?GQb`{;n}p'
    'M&IAyC34CDTN#n41`Dzf2bABUI}Q1M)t46DO$dF4<;Qzq&y`cFGs@(<bttG$Gu_{>opzOL9XsX#+vOde{LHQWAhGpx*!L@g_1=+HYSJ8bJ5KfseP|<3b;C!$'
    'YKu}1>ebz87%P3iTU=X0@2uylk+s4$e-0Pin$NTME9xo8;vvIK)JP=AaT<vdij9EaDV=*JUBZ{_H@h`&?j>C|f4g?it#lze>;>KR^xPQ!-Of4#`!)cyy&6=R'
    '_bc1#WEo%62h?*%rF=@bG5^lTuJQSV^C4^vw}amf-0kS;e)E~P#mi6}VqCkY_`L?a`J1hEV={A@SPGuK;t)QrR!^B2ePQ@1e{b^pSQCH04ojAXKgR0Du8bgY'
    'W~S_M`V&@++1|~}>y|pfB^Zd^@3pED$OiKI+goc^>$eSd`o%tDThCTVxG#2_{<FI1cc`a;Dq_nKj|j3*Mw2u-`90uryg@r#KnnI?oHs{xsv4NLaW51hjMw0d'
    '82~}0GqL;Cfx_h|ecsLO6dm|2d6m1fW<>HfSIX8D_?u#A(Pz_p7dn-@Ol~9lMf-xY<oIwr&(87(+R_E`;JbUl#%ASyHsGYV0~UlHdK+ba7GJfX9bG4*!;r2U'
    '(yQIk!?*Jx<RbykI*w4g8e4iFGJkcR)VKC`BJj+!cg0gQ2x<3P7?XYA&(*!Xy+BN9Pw`K0e?%48w~|)_Q)?U#)|V$?Ha-CK>q#%3n2#UO8%t#~F6ws`vX!Qd'
    '#nrzd*sxeF6)f>DRdJXg4<Kvsc-!ozSB)C8H(2?!2qhjAjlT`Xna%C4yTatJ<SqgHZi#Jj&cinTfZ3=XhBlNOZpbAehYJzJ2g-gcl%xG^@pRFVcA@fa`fPK2'
    'Z%XO0*)Wq2+UU-%=yw!{3ug7Rep~8A^vBUBJO;5UU)Yrc3>f2Nujp|{1{rU1hd!reu?BY70$V=d=Sn?a59uzKiN)h}Xj8!vmvZdVm%XD6hs2xsK8<G^;Wp>t'
    'gnQCxtuKAbvEI++q^7<fY6o`Row)md^wSBduEsoQ${1=Qe%Os5^;FQEcAx5k3+vpfw<r5pAN5=g5od{Voi&vvZ<^HlA(HIhs@H7gT~hCG9<N62xHv(`tszT?'
    'ToB`}tBOZpvxC|O(jSzGKbdNy*>TMD<q$_pu0?I^Ew0|%`QiOxKxuS-%kO-^oGZ)lz|hQvs+x@fTdOJQhpi6FMR}HOAC%6E#5s2wVdz0gfURJnmG5w@&Puaj'
    '(aRAOZO$@hsfLtDyY>~lob!nQdtV7@UsXA5m)7EIT?v>O(7InoIEUvUu~DUvLSLOf-cy>%Q@>ma-LW?uo+4uSfw{-?CE3Jo>hC8LK!cvAQXC9#^~LFh&5NGk'
    '2=ZBVyy5XOUM+5aZbfcZ!2W_i7M);PaeFE$9sn?n{<3L}qXk7o+EKVvCps}DmncnR_#>Q1;!j)Y<Sc?zASz9})!8h1l6(GZ2v%4UFuS@b-(_?n_A$*(WFtKh'
    '#oU#c!S7xToo?0DOO^XvHrfKBYe1`Rop0RpSVMKq;T&3<!BGdE&3njM)I67*H!ZfC-)=`}auDp<-VQPee-5k<x%vU>7<wgSOn->DkI0_}-^ICOK9bngtgYDh'
    'gc+!nZS>(16whzU482eCKi(c}@y}XX9X)zvvXRQkICMJ>vp_kY_f1L1$)GK+_GTBHbUxl+F&_=G`s~(lR&P}j*X%BfCJieI5i^tSyfXX@k#^&YuVZDBOJlng'
    'lZk9}yuL7>SzR`>7q_U<d0$(##^fS`h}FG%onG$cCA027#-AhGiu&?OKuytD9eirH!Dg)G8R{FpA~^Z0+UCHd;LX$i7WQb+u>U{As*DV$)sBR8bvsm=e=hiz'
    '?|9!Ga(2D)R;6-Ed@jp*J4!1{V6+7`lGK&j7cm1peCE*Cx7Z1c_9r+FrhM=n&<7pAZ(G%exR4a%1)Z@*nwLW5{Sv`si1SiTd797_D~I~7q*VjvRupe0gPHDt'
    '`!JO!r@xF?j>ky9(6`bbmuB7kSwxfRFhz&#dbK;Vn!a=P)$fi!Ixp&6as<W!?mX*BJNngm9=s0&047Hj6S}%=lC#l!HhZ+sdm~t$$xHarNSUathJb9Q7S7yb'
    't4w?Bcr({tp86NvPjNI~+MV#bdEcOZg$CGRpmNvh6ns4|>@rtshqHfw%qsY)x@M|EPm?<c44;8>Wva86hTEC^;gCJ)a7!Sp#sU<0y=tGdYxBQpFMDj)LegG;'
    '+gZT6S-9c!P*NV}-8S&^7=pv3;GXJ~G(w=uTD7M#7B)xWDH*F1mdWbsHm>Xa?hZP_JH;N3*75coEY5-Um%Jag*_Gy;$6_g#dc!1mOOC{j;a@)KGj(x&zD|M0'
    '7r^kJ*hz8n88nH_PwjNtd#ipk*AsNNi2L3jy5Bk_qqS{`dF|i^$L!oybtfw(T4_y;u?$WFXYbRh$-a(|hE+CeE0YWiA@$IOzuBI8=J3z=CINHlb<5Yi7|PUY'
    '#ZH#qEbV^TFYw}ecI{Pj2kk|>Tl<Y`XN!W2&Sd#IzBkr@p3iRfz<eaLl~u`^XmK05a~->GT!l1dW^4=%sm~(Gx4W$k;^l6-$UJ1_Va1f~bBJBHtpk+fPLD;s'
    'F2szF&)Q&}(<y$y0-@Y&N9Ju;gI3^On_92w?^HJ@Ms@l+oLPhgTrL64&q0mL=gA-rQGdm^CUBJM-<)oqZl>Bk55w7o-vi5_?$P)0At4vXb~`fVtT&d0Fz<0k'
    '>u|SqFd`-glRe+vJ^dZv&Tp9-dUNwKVnEgW9{p~DBzUrK^U|98m*%c=(EHzYSEd&eq}Hs9^Rh9_2xN2yp1R!v#7M`qVu%ke*!vAFklI2%SBUkpWJt5l-RjH+'
    '-iq>JI9wh{vOoM%H85$9ofDbha%f|VR(-L~;&=6rW<v(K)V1P(6gCNqqFZ);+QqNTrnl9=;$gw+PiaNFo}}s<z*S{njS_VgFHx2EtLPpWYM1)$|C?xZUgDiG'
    'vwMSAIdD_`+UuyhV7319<9s}9{|5Nwp%C0KMr*I$9Jt+)cjd$E7n|i{KwU0SdPyjq;O95p1FbcFg^siPlKxvBedVB{;^P&cKD@{lk8?GlnTomSuwg^kU!qw3'
    'MIT{HngzegpnW|#i5Fc4^qv{42IGVLfmz?(*%~0&)MLybOp8r>E4v_+9^$2fy+g69UsHC*^}TCsC<k4uOHw`|x6@={HInodlTqqt8-F;t4bP85LLKPa*(eKA'
    'X_yGt$;3tN-UTmewRJndn|p8`+lS!2It+>VR@MJNs+w&GjJVb>>gh0_1F!Ec&^q9OUFfM#OF8$=UJK|4)%sP!>301!jTA%&Q#DOnCYurE1^b;N76IO-o_lFt'
    '8p{692WPEmTZiAdIIY{-7|d|kSy|_2y5PFua;0%u+H6){r%_N<hsYKhvco^wTU8%ddJ^b91%_i`bmCNZuGS8;eZ%2W-nf|Ucjm4AWp)|+XB%DuWaE31mn5}B'
    'DyLwj)NQq~y!F6vIldkH>jl+nFxI}wA7gNrtf@vm{z8po{k<I4&t3bu1g)HQ0`g87ka%*&A3i76{SJDWO%{V1`~Y6PGr%Jkje<+f@rpO6Puel|Osx!yr5`<+'
    'NLqGmRZC|u;G8|%95>I(1{G^(?X%k0-9Pc84{j8==F?`vlFm;DU+2kJQhoT~c6vKpH%n)Gs^Dl?Y)9=L_WMGdL5@E|`E>-|^YgO^YRfP$;$K$hZ*67|MInP`'
    'ufZ5<Zh!ASSgMug7J$$?5Obr3ZcI*>*JKG>4*$US^1y9w$JrVGQY_d-t-vLjNy9uhu!>RJxvy-_0u9gR--!6Mim+wuFa7?=Iyiq@KHyqCQzP9r@i;U$k+^Q)'
    'VfrSwPktB8gb;VO4vJnza@n_kwH4=c_UFk_qqDRfK^iyXb9_pQQE~=X-Pd^2I<_vG75MOPrkyMJ;e{a>-07l1j2)Kh4T;vDl5hOkm$WyocMzduaO@Fr1^CAO'
    '9&0l9AEQmVa(+@CvYP{vz2loF{vB&9)Ahp*bUEs_GrkyMR%e|$-#PEP>CPBpZSBN$JHvIGYf6fqvEknigT4$D-VgTj)%3ON6w5oqZE!-(>(Yq^6`tc9hx<(<'
    'ti5#>Y1z9T=j`OWFvi_Gz8?(q_rAMXTIy4dJExO@;fq;R*#|+sO6n(;9LV<W5x@sNucu_JM%5;(&Th}~W9Mde_cWScdyk+KN$3*p=ic%45}bS&mrVLdzT;ZI'
    'DRnoGu~N;H>p?ojpLE-={9H{MClZdXdL-L<`JF`}vD$LfZ(Vl$w;g2Bxh73~u30hz6nyr2pI^V$EROVSd#yI(;En?*QJlsYXs-!tzB)^Yn||LfCWITiZlP+c'
    'A0uPjZZ+whTWe4WOYqim+h1m9eYUrSPju)F|5}qPBtmpdO)F&>*>k}9L*W9{wcYok#qICZX#&?z+b6>2WfI2K4SOY2>oiy|$o8|ke)CXUJD;#vWOs!(l%ePS'
    'C41lnr5C~BurjIm(M0;g=ERF{U$Yus#Rd8a8#5!mEs^348Q0^z=VadJ(E`3!1D(tJ_{VW5)dtIu?DYmcuasvuX4S4>_sNrtYx$LZf<O<XQQFxy3#8ttOwX9S'
    '{w|N+0(N=(LN3RaSJRKf9Q+M)AP7M#K?mpcRX;}LJ3h1<+NWlg#}#OQev6e5SvQn6yi$LRY&WOb$@JmpEIp5`-+I4NK4xo?>ODcZaNvHdc!OLVT~WJv;a(T<'
    'BUz2j0^)cd*o?AD94#cbcV(SbqY}qX<*^3I<zC34N3!D=Vw-_!ab}M7wZZS)O``1YAsO6~0KN4!d3t^I6ZRK2Kx<#MU+8S8OtE3C1;y<?4!CZAesyng_^6I%'
    '^}`X6fR=Zp<;}U{Q?ofPbw!Uj%bC8s#zq=@LreQp!OiptOZGGH1T6gHr2j7>6(tY5Ie#5ahA8DQavEzVYnfjphgbZzb>H`2g;^J-)ubqbCN^&hovl$__c)EJ'
    '#|+h2rT*em3SVLJsT_w)cbL5e)2z&A=Gip`?bzB|%)$Zw$V;G`WVfa$3cSsoPnhpWY!WYOi(>XXE0+HfmQ_UJ?}Kh==>4lzIi_OK@*m@`KAvSP)Vbt*{R5|l'
    'ov(X8hP4PkGX;J*#nQAn{e$3Lt7PkBgEv@%kg|Q1KM&E!hvYdu)7iXy_Gj9rFC0!4OD30%#6NwM=<NNm&a$c3I%5kv+$PV>-FQ`Jx64-rE9Ng4*)LD0zGkOj'
    'e^h&Bj3S9(&^s9oVl>ES5uCNyQIlJrbMKFV-%KGCByzWza=_;2ym-VXL(2aocSDbF+lBES2c_0Dx&!dkKO{-$2z_zhLe3xRH1LE9_bPtN@7{F_s0tlc>xv^R'
    '&0rmdl|RLrV<?#+)B+F&O#876m_N$a%fxy`j&p_E?Q_M+22ooZpy}AF7R(GlGi>wmDK<>0)nIi8b*gDU+YYl%z|n4rl-YgX9oF}uh4wc2ayhTRguyB2#wi3z'
    'qkU!O6?M!1$l@;|o8*sInfkox&^On#;n8OZJtj#*FRIq1Rd39ib^Hi>-CE_nj|lI4-`6T(oV8>@w4-tJ=YxM!C<Cn{p`GX(-tE8>lFOPc&I{2-zjpD)r;pP$'
    '0l0k;V#=&daBAF{+%N59*Ly$Ejsbw!c&y47>kam#7M_er)TH%dKo}6bS-}2pD2xxIvq6oMY)xE_?TX&;zOd;$G4d*JR=W!|N2U#`VnOEqJqr~hZOA~H7A7zt'
    'W5>IaozfeqW}rLWv{7Q#?f!!g^RT6oP<Gi>!CzW=r|s#fc7%fp%jk<p{N_9adzQ(K-@B2zthVC^1s`VQyBUERaMhzaVi&=zk!4-5Z*Wks4#;LE$#<du<`}aI'
    'KONNTSG|e$72WYBd6n2xYTmcq>R>klPoQ_?&MbfT+ZWk4Tcf<&ej`1VrM`V}yG=TO9X(=rsNq%4;ew@}v&B@YdJih;CZ3`WCwQ^t#m&N)5A~&&q-~@($-$2h'
    '64vS6G}O$L<7U>_Z3hfBOHOL**iIXdT~WgoOy(MD?)~)oK3y*<=>~4sYn&}fz%BnSyCVw&iwrg|a%#3`H)}kRqR=0v{kUJzHM{hZ5UC16mA;<vdFQ0;R^9Rn'
    'vUlk@s=YLaUsYD84`o!&O<`U85uNL|S~q#>(=;g>9yabtr<tEw+i-V(iT!GdK9W)386LFH^n=v*qDal$kaCRR{b~j0)linewl!4t^P6=_*8jgj|D15;N6CA)'
    'NdTQmPdFyMV<7V7FUD9Sm^P+Zr2@}7o%il$l=*eO&+GF`TgHwNW*UMmghS&5i_gWi@2&Bzz<#QGrLjLsT6sd+S-N>wx{$FU!bks4>d2l}O%c2hK0=#sMwR+y'
    'mPZmy9|zYLe(5oi<~{&=)aY<S?TruLO<)J_V@lx(nB`By8}iqV5Zg@`%K17uUdzvJu1u;Ayy!B?xSV(TS@7&MP@hCjf;P??jroJR6sz+NAFa*WG@P5zktn8p'
    'et1@Ke&w!Ti8MtOHX%FFjy8RU&7M&EAtlp%o#uo%i%;!x305zk$K58<Y+TdsmYnV1o6d$&8;Pa~^6BL__xa#vFD*jVNRtQ*GFsoaLywp)ca4)eXy<;lvFgsx'
    'al-n<X54Po0%3a6Z|L@su^oD>V%?4z{i##U>fO=hV#u|R3(5e;%dPYLtY5<cR(c4qouYq;3iQ^Ua0^y>c`QA6rK`xe|8glF2lrrIn~Zw?l-P+AHyN(Q>Bir!'
    'vJr!L{O0|8?UldEX(#I(1*OA=>O)Jm{WhW@)q1v$@9yIB9m46Q0Yx`PJDtJB_aeDRyNf1i=UcyL)8Q_Fcwy%?y&w5<0uCyo#dzCKrpi-u9!KrHFKs}ITHc}W'
    '<%nxPig$zCKBjx7(J$3i4f!;1!5EH;$Bct+LH)9yx|^$cV*MXE(HftFCe9VP5WqTs+AWT?C(^W^?4?e<J#D@N2AhZ@4qz`$?DM0$#bq~iZuGUJvt#qI--JLz'
    'xWLn~u;snQ`o@*RA#|?lp;8}E)n)6@fZO_Ju^JF`T@Lj6JH8H}s#aTxgQJS#x8Fj3kQ81SfP5l+_k7GbO7ZN(tcVxa_|TwmvGH08t(&Em-cuIl7FwL&FWTBA'
    'Z8FljJQj$j?OjZPl<OT_?cT5T*Qb$p6VH#m0M#zU<E@0@9bdXqB?1Q@Bu(Ad@0iW*vWQTw_s)|kx^4Fsa99McsNDKaL;jw}Baz%4oh4=;NGt=;(fAy-hAhAQ'
    'trlu`S?Q62S;sbpGKcVWlQn8J3jVl%YDJz;T9k}Jpw@+(kC(D&I@6(lYObU<e3f^f(r+zSC1Y|;YfH5S@9k3Y=n|ltcwftV4<?-=JNn7IF)GpDyWddTq0y9{'
    'Zp?I1CAoUVF^sXqO>oB`_t4O)kQ~1y_+w^fn1pXNp_g{c!O*6&p4J8(#R8|nO>vGZzjj?eDpW?kC&2IR!NG^#Bv_XA;w>L+g~Q!iGpls(*ueD(cpi02J`?{#'
    '32xmJ6K*rP9+={Aq54nU4v@*$Uh-G4%HVBao<8c{JzbM}G5;PMuD(y8sZr^^)N1WfR43eLTjkB^26QKrDSB!=<f?cqmaFNY9uIqix7=wy2bO!CsRw6s%^JXL'
    'P&WV4WdiWK+5SC;Q0qEz?ii#DtM~PJ+3**E;NG2Xwwa$#WQAehGA&lv20&i9PzIoMn6$PK57_WIQ%|O93|gPvUaUNT8_-oS`Y)GvAfy>|r;b%e<?pe$0llTe'
    ')VF$-CImB)net^EnB6>S8*8V4a^g%Q^v-9J;s9)W&-!NtnbqvM0tCY^sO`F_)pJids)q5l46-1^)v>!PnUEI|5R)#SEq-z&Dk<wQYy{}oe?Oi>ZYb4H;Kxiq'
    '7a&p=vdRA*&^cnjomgk>6}R$UQpX6*q~)rLmQ5?%%4i8LfE;>74MA9Oc<JtC+js)g;EMK1xbT3dpI>J;>T^0gYyT)Z_on55Fb;o~1`U~JP^2LxsgO>R_(MrW'
    '2Zx+09X|W}ykB6aUAw>gx|(%+;DJN3<`~!d%21hC@!25I-;m`biy<o*ep?%i-E=T1f@%tBwmnR@2u4k>Mw`D9#D2Ty>mQ@yIHv$jZm)!bFP}Hz5IuT2g6+`W'
    '4kR+9R(hp9%N4Tb6)$P<=}WtJ7!lR`R4`+05rbZ^fdB>D>5sA3X@|Wz|HGizT{CPO<+#10@1zO8Sd0A3mI$bo{N@wnLxbur6szB$$qCEU%Jm%#1Cq<IOEgZ!'
    'Ypph~y#B;!uN^E2A_D1_O$uz+NU-0F6T0it=wx(Fd=0~*8bCh+T_id3k#1hQHVAxq&_w1)8PqtF@W!6^)Xw|KpZ*7TMkenFV8537o4Z=9mLZD*jwWY`E`uv!'
    'HS`${Osej2P3rKGpcfnK($xOY9$X`T3DiMPH&VJ>jQ5=$ZbL$cN;qD=%C7S`dB2DMA*<x;%70d8{rCF=KKjLX<*Gij8D@wd7LBqekCWcm_)CHhfV`befA0$7'
    't6ukRYeuQ{%M|%Llh4zL?kXpweZ2@@Z(QNrMz#BfS6Fy`$M^l_d|x-YaJQ&tUrhnlUb`H$3nOV0UtrMN=6}v;5*oYb=V6Wdi|(iQ+uwEh7w9e<+`Z|2F(9`M'
    '?|iKt4ZDe=D3a%N+I|9Sc-?EfjG`w#?!ZXd<oPOLdRDz=*8mjOz@V9w1Tm_^?XCmgXO8+*KO7jz4TArhoAt%)K%eGVlX3s_R~;?<Nd`voe7!{`Vdpv9rW}(x'
    '{`OW!#uS`Cw2w3cs^4@G)OmfpQ+G4GJ9w?iwsqh(8nj%=*IIZCr2kh!)k8O3uIOaSO+|7cF>AuhfwQrwtye2<HES96$)daL_y8~*jb-!UG*KGasl25@r8*1A'
    'b9=D5BG0Fh=r*AWTlTLc@8v)Cq>I(L`@{vP13}K#EV$?eyeN=Kc8g|}C8_5qqaVoU(g~l(Pv2D6*ZXjp*EeSqL?16gO6Pxd1>cGjXx|P$qd^>Btzk5K+@WKv'
    '!&4EFEzf+`=7HB7w^C}Mz1SuE<(qHMqu!^5v2_y^;5LVcIz8*nXCzbVa$ec{^>fvg2b;S#67mrrkKA}whvg_Ev0@86U)Bd1wj3k|ZRh)h?%E5#hT;CVNI!xs'
    'Pw!q5S+(UezI_PRm>&8C?hUHD<hBp4Mt`LBCevSpD!bLA7#(-F@qD@-ZLVU2T?xi=)(M#27U)_rJe${-js4VNBD<=<+YNqW`^{H>w4GHONqLstaXwT#&8q(N'
    'Q}sSM>UR7-)V?_TKp78e7X|-n^n3XJS6M88=cM_(W2`F7pN}Ny%1##B@3oZ-E&euWjWr=`UB;)0OT<SyxZ`>o9kpbFa_ennK9$h|T^kp;8g_X0)tE$rXx(YO'
    'h_PQe2J)HWcI3?#YGj4BU&IBuGo9cEAMw|2bL?B4XVqxAq#usycC?v_&>zU2+`V_^{38IT!DLr5VAW^`*VG@R`O|IL(Oia(cXx*G>IeXtNOouOAO%Wf>aS%0'
    'nrKKU!i~yh&W=B?hZIv?VdZ-ztSg^0Tq{Uriu`dc-LwY7VCv*6g}n#8V~E-ziUD)WXv8$^93S(W7UH{E)9ijS%$?(_x0+;s&#S`@!gghAX4hW7Kl3n7_cyIa'
    'V@6)3A%XH%qwOe~PXBrGHNu78YR3=ADKUxCL1z-)7eH6oF`N}u1ESaM7*EQStLNTfR=hJdgs;z+_j6rSsSXND&B{IAgN)iAw^xN{rCIIQkH;N5Ov~i8gmGxy'
    'IGdC+*{-9P#u76L!=!tQAz%9?*KZY89igLfkPQ!*$^|@GJ2{ht=xr;^_uf4WPW73ujV4+D-Q^GRYMkwN6ZDu3;)Yl4RyOz)n|530Bh$D(mFMV1@?_-2X|rF)'
    'TkZ}&@o%dL8h!BuxZl%cDJ<2FJo9OD{%n+u`DRyMq)p>8aCD?Cl|jh$h|xVc%k4C{XR8^oJYCqZyoA%P(t0S8WgP}{QBsPjp6-Oh^<-|(%yC5*7$Nt(iRV3h'
    '7D$X{6uQ8%MbvmpGsKRwzgI`a<$6ix=mzORSJFy*q^W1e7U!$YYu}^>ZR^>2>nf_*tG0RUo3%ixbbIqZ@f@0iE|FG0Zn1A~Tdr6BY1<)NaA;5IFIs7^bFPZ?'
    'll1fR?!d*}=(j#6Vd=dNyO@5zKd@gO_>VRsqn-A>PYe84a+SvKa*vGs=5}qbbw4c*^Xi?YlCz8ZE&74y2NN`4^!dcs=01MtBab0C0rVHGG4Z-QqSh~vvr{W_'
    'H`RGCx44-}cE%;U-9UENKA_6n7&V={%gepjA7|1H)h)zBfY|s?Y4&sDa6250L_icPI|VSFPwYXg&UjyUH(3N(GJ+E7ey!CfkUtnNKTVW>SAPN6?PIMzs>=!5'
    'zz;B>&b@j7UDNjG>OA05npRXD6aC)2(roA9cA%}b;+Uk$6KPgnJ8fFINTO3mtLmhl7$~)A-MdfS{;Csl8~YUb{7NMLPO4~YZy#+CKu&PC(z=H9{bATlC2cFE'
    'Q@`kKr$PtEm;fhCUK^9dgQ$r*8a1tlJ>N9-hR}@0ZIJ{Tvps=kE0j?prCkxay6#Xtu%^r>B5v=gsE!e6Icc>!WqTO#hb})@kvsk*b&m|c|6?m#do7Y@??6dK'
    '$HUZju-z{-@-xd?FX91UJ!ouv`R`EgnXve*orgt)lO)DB)?e&H3@)1Ui{xT%ykmZ1D!=-n{qtJ~_|mY3l^b82wPt@E%<l{(<mKigArjBSw@qPnmzl(abryJK'
    '(Uwn1?+`^g52N3jZ5H}!#*uUotk4}ZybkeYgkQVoU)r2f{MKEf)}x>AcQe^~anyIKXU0e>#y0bG0m*Ey76zQ~vvOiSV5yvPY(u0rXf4al)Spde{^V<|r`rwH'
    'yHBTu^yd?}1ZB(pls4qqW_+2iiu>;Q*&DCrx>f(3Di@|t)h-Un)8IjvSI0B@{CQZ+m#5fP!?yV^R=E8PymCsmT-|#femERNc(mNUAr<U5q&OGF;VT)AB~Gdl'
    'G5DO5gnh0(erq@aqjRsF4Dl`UR)TySVW-9Rs}mWB<flrd>ctdX{w8anx+ou0y_Idm0ujT3AYG8gPKL*Jb~9A_G3?R{Y&8`t$=a){c|#aP%L<>|e7PA$#ZDf)'
    'VYeCqSXQa+c9dNGnD+ZsUsV$({qDlypcB<h<8Yz5(YK8I2Ccuc@#j}>j@5o(^exuz$}7j&-0tH$Q%1X+G`(lZ;r>2)yX_Bf-|0x{-Ff=ux2Tc$Xo>L~>fdM$'
    '*dFN$I90PrV^eqDvN#-H?ak+xc1ncCs_?dsJPAw&2fU3=6!*-8Qf9;1*qLuCoptRAZAN#vO>(R%f$Q7*-dyaf(Y&E<7UqhSqm%dbfCDqQeVeZpxQ^GZT+24w'
    'yBF06BPj$mdyt=@nBdcP?Kp)nWvBgRhNL`%O|`Q)G)}`vcqha8xqW^jFB<X4r7j-b)u<-SzB{UE1T2JBi7SW^NQJ<MDgFo8`tumSZ|#m}<j9mekJ_E}@_gjz'
    'v$Fi|6jRjDTkFsaxu`ttnMw;O8!a-KAIFyorw#r{KDL?mO%uHIl_Hz##gRc|v=Jlp7O89%AR1KJYQOf^)go<8%YlobOTXpfZvj|czwGs_Ods3TsMuGHsB(Fq'
    'f67UH7!BlPpbgaEJ1PP!;|qpe$5FhNV1?B^VCGcC^qa(|M4z|3PqkycDm;V5ZQ{PzRQ4rxd;-9qTcE^nts34$XPta9-SwTpZ!EPAQ2F4j5n!n~jTN(J<HCqf'
    'yei#qo$sF^?Z}Ak6X)^%g}A6i9s2Cxp&<POwFEys+;#%}=FV$xRcY1z`|NfqXT0<Qm6Qrk<#+hzn#v!%HUhGa%$(I!@57|fAAT0~q-hp>W~kbAI+$Yh^O=hW'
    'TU?!PD{_rwD)6^Ch}xV)u7*0(lPW%iC(JW?q)K!t4K4JoC{@84a`aJdnNVDRAW`z^o?$OnAKcUF6Rg!ixY+i$^tfx?hWP0x)Yco4GvyAr$r0i-oS}_h-JFC7'
    '2VCc~%07%HPn!t(^4u97{b{EWmMHQ_#cFd0bscw&ij*q76ZSlAn`>&pNv<;4@Kyy_Kf&+x597uSfQ8eFj-B$J)c;HpuWd$)POBo`8oL+DX}+yF+r0)?KJ&g{'
    'eru1{uDwR|ZFxOcSKg?xve)l0bEGqdUPhPha<^49@G)LbwRzaf?*2$0ha9(rFEg{=9n)T|-8MW_ke7v(aC`5Stlq|<s1I-BgT=37tJkEm9@|lNt!_2c8mV49'
    '?Zzm-Ql0ne7b2GMMeAQ$3SZ=6b&yUByFZYoq0HZlTOWQI!GK#YuI#$HMH;i2Rd+v;bkSUt{Wt=J+`akh#xGNTZn@;+uJpF8bX`cpUN)wP6qv^;)ZI{D9f_M#'
    'XN6d^S5m`Uk<}Tr-KZ({4QOrMCV(N=B+1$@dXA?m{u$6#?eVe%vL7fuh=bi|SWZl_OJ1UxqPp=H{qB)8-|NZ6Fr%d_EvIw!0(*zyGi4c^JN{Bbg!=O)NbcsO'
    'Q;2&x=`XVf@W!Xrq1gHV-=j&~FH75B3+=?71$tanPs^V97d&PmQrqikWdx&_`_T*Rfn8Ys8?Xe&a;>t*_f5WSuFMh8<HuCN?rA4Qn)~<m(509=`y0_OX=~cT'
    'U{x2x1#W}aFF%-t_Gcq+7>pY~5unETV{`tVz?=SOoG3Genxo6U<(i{!li#`RvscWk;J$awW+Q7xJhCk5QF?nf+Bk=+AWZ=#s8-b@d5ShwU!C+I79UT4&SJN>'
    'Z_km&oU~vtopAG9zfP|RM>m)K%yjEy(;Q8w?kBsp9ieV)`SSFjy<b)~=+2d#_KxwVqcY&H_<yshXEx6LZ*d#CyS9Ato*yqn-Vw)ZG^V2GvvO9O_<j+!zUKbD'
    '7UWq(0T}lZH|Y@`MzRrui~iG-LJgvQB5c0X`0@k2gS9|~c)Jd~`g*5e8(kGX$7g<FND`r|SBB_77u6Ybit#J&8<U{Fv1bo+zZ*?iHw0pa%P+~JWpw?VI54+e'
    'UHuX{W^+Nk%Te%z)1%u<)%IiDt<%Kpo_sievt78Y7<zKyiOMmj->o)pEU=}WA^c;iOGDV+*v@WLeY<B_m%l@KP`ljkAT83}Wka`F*84+R(dZ3vcz?J(TDoig'
    '4gFZ6)55J|gWl&$y0@FaABIB|#<tS9lD{5JNmf(3)_|aCuR{OAT5EJUci$0@9w%s<4aq8V5Yj8i_|#YA^7>TzU+Ev+0fRJ-a0gD@dU}+5*s>OqH`IUZiy1Do'
    '<%yovqUx<hJ!$m$CP9fj_1cWP>v``h<1PGd5oR%&(p~X%8~$&^x<dDTGj32DU$kGJk3sgZ*~!Jy)4H!I_W?C)PPZeTa-yx-Cl+sMe%V5sd%a@ES!W8de*o5b'
    'GK=kk4nld|KW#fllHPP)rf7_5<uz2~%J6DkzN?iGpD)WLUqJB?sc+CAl~)pPpA-Vj^946c)xnZ_JznH<d0KPfly%Ot$tOsv)KC+iUah(CW{YT3Bh<&#b)N2@'
    'P@7Ko5suJBD~`df6K06L(q^S}Sj#=Ke#FKus#}V#T~|`rg``5c7wvf;mmXSRWEFhltE2GItk!x4N~-oJs72V_fCn214eVuW@TXVPDSY`<_Ial=WyVfxzc}5d'
    't7%qSq{m^O9>F8$J_ku2RO6QW86lP9JJDPy6bT^uj7GRnoF~1Z5h;72LA4}pRLQDu-eAn<w~qbqmXU!cGJnI*Y52fncbD}GsG<mV`#88y9|rb<WuZLQk@Nz0'
    '#dDT^ffp!%`z>phkteW#HlDJ@ExOJ<n06)i!N`j<IVb+4Wvx<V19-02d+C>71F_N&&}g`A%G)Wm;!YuT&9)-|nUBc+$_Lm3R}XK08+*VU-(Bb1ETcIHbQQKx'
    '`S8*VzfLfy^#xH02Sr}(1MvDmG{{;GgkN(mnk9fy*Wa&Sy?j6O%gH=ihd9j2uH0NdmmP{H>1!{Zbtaqj<ZL|872nLDZ{<B};eY-}uV?#;8_=ojfa_-$0Kwg8'
    'SOo8`F0P7Abf?o<hqP|8GWM(QO3|cBJzGBY_r9lE8_~{__|;%UH?e{rS}oVt`-H#KeZ1pB#S4fkU+nOeP_}x#R`gD1XvRq})eY(Hme-EZSHS=6t{*|;(1@H#'
    'uUSH!-SgHXh%&PDCwHiUI6NbQC-J4lLp+JXPP29J#D+63iD+@s=7aj8uFKiARtH-5-Z8h7P#j5zexWw0;Dd{rFOqAXv>Z`3k0z5nf1?=}l(TyNr>jq+?1=xn'
    '8^t|?^Oy3na$+ySyg58R(>*8720DIC{wVZNxh;0USOOq<lwqI<D1Y+eKf`3$RSl`KEHGU%Z(r_<JXV?4Z1Lxiy}NtJnN|41K7U-#4eMq6Io)#o$boKUdaVt6'
    'c15k9j>rGazJYP7E^baGIjOrq7t0kV64k)rKCfhdGU|WiP;0hi($-pj;T8RWsi068?T?S+tT&AA@5P+44+#CjMynTg+xTZxX?;5^>EVy}xm_#|Wot<PF7o5>'
    '<wl5dj}Toj!1o_O?)A002s%ww=@*sY&F^A;`}vK~>34-(T~F`qMQJ*`f4-+@^XE>^Sr15BG$^mLE2@C)9o+#RtKIfOVBh(sGh&{h{a^y~#(}gA>5ZJd)1M#l'
    'Tp7OxY5%bpDMgU#O)@FnY*`S!=H=*MA@O6j2fvRZ&Fhl>g%^#93(le)a~#%d@5SNq5I0ml+V<+?=tc(zzU(hlsXT9lmcI)YPFQi+Q=}6(s0kd!b{)V})7g+Z'
    'li{^>v|C*oxIe`5fl2pe7f2whUg3M|4_|M;mzDL5nzxI}V-MykW2#iPZMxCJMrjXgZE?U$%o*nuSr9!AK#5V`?^m0ISX^OCTixAJLbB_AbuL2LX@6uSNXex<'
    'p1EVbRkHo>yk`sd)Ru|iwc9`j52r_T7Z>@=yIMnlK6nkEEY^5j%4YQVRIbfg!6WYG5daN+1e~6G_*^blOadRXR{0i=2-w)2($N{bZsAe7IX^CFx#W>HHZnH-'
    'vVmDQ@p;h@r8=k|4ksMJt?ZCaE0ARjr;S6P&BmvoA-9i9wl;cXMrmai=1;Zc-7K1~W^blJEd6L<wfGlZIkxfHeHU^2ar_xbPnp+4Qj@pF&BpWFs3ednIiA&q'
    '!&U3VX50-P>*!}`pkWh4_ghhUrqs54hP);Fe>kvcyP!H{GnA@ZTwNibMQm0aoM9wsp%@;YPbNZlw20_Gg}gdrFOE-G(teE(9dEBxP7mhur+@)&B<bZPG&@fp'
    'pUkR@)p;|VjOLKu<wgEg)tMXC8P6K}Y|8J^{0y)FZ|<(WYd2v3Mt(XQ4p>KbxEm!d`XYE2OKxfB`zsNAxJ8{gSZxqZl8Of{rQi?V(M=(~QF?a8CyvL3*0aR>'
    'wRT`@A^^8`+ZQ={nYndXhxSD`uWrl0xIz}eA|0HL@Yz5lg1wQq>|W9_VebcU4?V62wFehrOb-cuyn?3Fs|5fFW1W4gH<>5ZcZsu~CRVg=gt*>}g+=k)P9nJ-'
    '>aFX0ts~!EeLp<mqt5z9elBS;JJivWJ($~zW{QnFq`g1)jn^eJo}(;UnIeTh%s{?Xs#)~)?(Teodx!Vefa@?nN3N$niR7fJoHAmd(3K1MR)^Gf=9!ne!@phR'
    'rJF3P1jmJAdG`JIXxCoAapmja8Xk;)D|9H|4i#-VG}%}AARXefeES1@Y#Cm^SJsUY9QtsZ+Ak)_>|JypiTYOE)4kO89;aW#?PTuf`QITMG^^WLb?7Tz%%nJ%'
    '(CBryRMb`>p5ANi@fC#b!d?Q_HPthh|3b{Rx)$i5MYiEyeD2k5ySKVPS${zHFJyO@<zi<5HRb0#3>%eoylC#{O<8PbUcJNCF|BbNF}K?!S~H^_IJ}5L&or^?'
    '9BWrd4l$Ma6#lK_+O&#%RtLSuJ_`s9j<1QL-^s~xzwUJ#lxksYUF7k0*9XFwn#Vgsb$DvcuS9`<N3{Kkw3$3O0~vAr8nyMP(x6+X?V}(~9GDRkI|SHo^q!7d'
    'P@~PT3YM4VL3*Avo7>hdhxgC`C1*>#z)|y0RPWJgHEgVjdQtILv<4tuDlm`sVBhU`2j|To?3YXh2%m>>e{)XaXf)|gE6&!b1e5J(r)F?>NBA!R*hDJQwpe>p'
    'psgj-Z$qKkA}pkpTwbSKDYa`SN$ON!Q^@Za7m&I~5A5Rl34hTP+PMfX#Laxi9iqn5ZTLabLGn)RD!Vn#ZYT?uxxRD(%Br)IRffDXnffNwx8b&Zu1!erCe7(+'
    '$x_Ye*)J}R%8ws6VPad+vIh=;cr&`Udh=PD6E9nmJ5Ojg(oL9Ml+&(2wvA?JGwsZuozWRgt#lZ|a+sXM6=Cee+KXthBjj8&e;r)x?~L|e3VaU1MyU4jZ79o~'
    'VmHrmkS-4}WaCMNtu`G@11d#O?9?3F+#<>eZA(5E`1k-PNT>FD?()g6xd69IyITiW{mYmn`@<(>w`|9|iQryR{QMU0FRWuAhjKFQ!ra#XiMUyhZvz(1GG<OM'
    'YMZ2wPgHWCsd)kf%6o0JqH}F3O;53N!zRpH&l|$Qjvsa>udrS=)d^=q`yTb(n1{6;mXrK9t;WsNlb#VTSLd(AAOOp92)AI0SjOUbU{xF3XcunCixTbP#pIO*'
    '^J30rG!<fe(AlYpKAOp67<8`gy>1owWBS4e^rDY^7Y8b}#R(}_2xBg*@$FN8d_YeN*f%b`O<L_^Ko=A9*4;AaciQN$@FZN{Uyb-_oy*H^T1YqK<CMY?d&2^G'
    'l*4LUU!|A0KA8Radj!kR;~8W;tZ^;##v5Zh$-@tYtGH4Or}jrU@<x1F^)_~er=d%}GsiLZvII56X?&zUX`1dKVGgrTvB4S1a@#pIxl`V&*M}jo-yWYVLbkNa'
    'dV3kR%BY@89~Lxz?SPPWhaEUfF`B;ffh><A<S&goYGe%b^Bcgn5h^xCFGlu%8%h}IY818Z!DSbhw5hbV<47*2HU3qYz1&5z>?Sxp{dc^_W>U7!EpP{U#m=*4'
    '%k*@wbz17-vRYVN0`|mbGg!M<;!i$pY0_v{dSg1?(L-?CYYmy9wn2M!n=MB_K{MebJasPP>ilO9Rz;`+dlKsk_70jmo22%Mkf44Y@pVtu&Gh(M8>cA-%{ouK'
    'N?mf%DI!k$Ne;DMFpxStYI=Ry@2^_*dwU{PE7{;l{#x;FjV8-}3{1k#jUC)tlGv#Mih9sGkM<0unC)qI{b4@*=T*>r`0T><C0<Im^d?k=@#Qes^6zDS2BVRe'
    'XtCNkHa_gCo_?HGBGvb;lHjuoS*r@mJ9CbavZ#6uoUZ6L-!m=lx7?i3O>eMoO}LHK-&|S35!wr_E@QxW1nr}d#q^~3+PsYyq2T~Gs!iEyiWt=Q`RcsYd8p;}'
    'B_MQOV1B88BwsTGq+f5rvo41WGF@91f6qgh-^W#Gy4y8-qtoPeFG(7CsaI4^@ke?(H}Bv!D?7@bt#?1K7X%%_ugt`r+8Kk$W}RdUN<Sn$vW6y4?9jh1D-gId'
    'cCe-IS7NVgKQd_ZgHPQ3sa=L$<{<jKUricWWizc7u&(i0Bw7yRp0E*#90QiC$GcVXT^O$4S!#ygfkl_i2Vp$jb_)M$KF?%2%f9$tS(tK-zCE$l^R~WFpSv`Q'
    'pf+5ae-BFy#m3&@56jlZFwnAV%GFOIP&gH`j@iDtt;1>104ht5d7O1rE1-LG(SA0hxI%x<H7uN-M`S*lq2A)Uaf9#htt^-UwRpYotaWMf3wNykEo{x1*m{9{'
    '@7{By_110t=2TnMIL|(9kBE5dG#VYIW_)Q*J%(n|PC3{oMjlarzx;EYfn)BoDw0poPHqjHD=l?ka{Z}?Dm$3_4Z?40p|H6<Cj4`!+p(J+ar7RTYwVajPhkX#'
    '5Mva){XEzZj8^LU?mF90er@=foX>45-)YzEm$f+ayK4;n30h-f&Cy5pfV^UFEVJ66hY|A>R&uT_Ab4DO`EPV0N<FAMOE4{q^OA0TCRt~667Z4bx*v*Y>|b?;'
    '04w&<oLu&hTnnc?a*_l1qj&8e4ugHV|1)uNJCUocRj0Rv268a0y+-Ov;IA!o`*bfq+}++B0>ZJpB0c`VnADaXGTae+kLcC`oFCn->8MfzfX?FswU_7H53kqy'
    'Iq+DhPD)xk99XXx-nty%G;mbFDQJZ?q}GO<tIXNC!3OrbGjN&T^`-c{zOW92+Tk9&vYm^y>$y4mzOCDNvs(I<cc50;Y`p!AR<KdFiUX#n3{XMsv*i(w{xVLc'
    '8Kk>c=6CmNFnAHU9_eeZYYey1&+$50j6N;sl4F(cwoa`A&3SAHHM?+~dPRmQVM$kJmF0jny8(YdO9=Ok?XT;uvD?eo03Q~XOJaf6!<*4-s5+yYTbDRBJD(fe'
    'Z4fa3nbaAeOY{M-pvmFU=rzyl#g>-*_jy8Z=zEs<%pDo-FuNIk#**H;q~7$5c%kc44`}vz55wmwQPkm&84|fX8YJTt>-7jO@OGW3Sy1_o#iX&BcVBhZB=9%b'
    'yv-~t`<v@ze>=H&t#e<|G4fKZ8fn-y4=0PoQTjdq0Jc{F7QI#-+y(8oJiKz1MNx3&d3L2~e|nai^G&olSM+#teh-yx(bID014Z9%{jo!O+~QtwIc+$ZQj(<>'
    'I61M#!)i0fR=(Q;=I})*75&-4o{tgq>W&3O-;bM)lT+3jv5=4)?HU<7ek`}(pODSK&0k!0Wh0o$wQ)_m91w89)rD}UU;|J3j<m&nH0YN@W>P!1g`+;KDAxWD'
    '1W*2HlHA2VB(asEK9hi9jrT{`aH>VSDN77)XL|y$(`bmhr}<s@+&;_mFj_e6?=@ZZC+sL)V7quVat}kczml*LYbzh+tMqTlbUVC;7i4hTWaC6pZZCNRzI){M'
    '>pYFZ@Xt_H`2Ts3%?Ty~L^`KR(fmcnRe!HJh<`oGY;Luaq({`U3vV~}VLfEvoQ=-8sO5@2{om%a1NR>lV|GRw!%x)teDlq&#Wk%#Wyfj&3wF>)S9Ek?jVzJg'
    'bR0rM;S1B~x1YCXCrB-bCW0&eli9*m2Yd%dBz^E(d*JnsuW|Ex2Vo&kym+BYp?R;yxjZSwHORCA^kJ%l^4f|o*>3%%?rs}@UC92IsjMx`DTMK>hBLD+GE9rO'
    'ruf{refq-|uWu-$)qxy)>r2U-2ng>D?8mFDTfaNR9au?>9o(VI+Lpx{?!(7k>W+6a(RL~ok?b-@$a?Ri>-w{G&+oL`L)PcZGOr7Vg$aOMuq@Mu*bFJGKGpT<'
    '>CYr5*+J*dL||L@?z3%-1b4jAPnE73k(3go6(bRK*LV(x#X~<h+wu+(>&ZJ5n?u51Lt^7-bT1>UTr$wiasQTlBRgWnmW#vq`#7o_cVAhfkI+}0&728%M(Ev6'
    '`4DRGP9!YAs0ddJuRlq&N6-GETE7l9rrbXG;NcVka#VH4^-g-}Dy^E;tGxth@M;jfHPK|*ne5U3UwyBm6Z<au4{2K%WMv|=CcHNX=SEZ<^3s0(y2HygK`B5F'
    'AMY2yr5!1!$kmt{@Q=;)jci<QJ#&s%y|L(~-yqcNSGz8j+y{=!F>A>M%}BjlTvx<7D>MCkE-Ruyog6wk+iG{cFZnOuW|@)o>GRaB2BoHoyrb4c4L<Cx?JsYG'
    'y4P&z_!UlTv){YZ3QyudBjg}5;dzhEs=m{?mz4k64u}KEK(Im0>yWYVo@hGo<Xg1}Z?^D?cjg@TM?=BtLBqluEU)=ivwP?X?y=Eg*tmZ5<3dtKFQ}~i|2UmJ'
    ')j!5*fS-|XvsLs4fEX^Q8>3=Ci|<>$&$NI2^By96aG;syFz$vc)x^K%q_Z7NIvO%N3+8OmsEu#QF#yPwpq^?g;xg*?Nxy)*Ieco#e<pbe#*h<*=JXIkEn@%L'
    'QE#L)KIfN7BE;25bjH>5f)&8)@w0H}aB1KMmqv%I*~;H_3RlJ||H4@R%`Hy|{y6;|O`|DPKEk@Wn&<7|4=mV}K$FfR2mGM@OwBIf5vrMy{s=_O@fHf~)`A$W'
    'v|vk)HPAqjaJWi+ZXkTTX*8DeK<FG)wkpiD{>N5M(%xO8@DAF<l`suIGkJIRaP-tnM<puE|7tl}pE7zjV;+b8A~OtV5!aj%VzLvF-uY8|Ilt}1IT6cdr;hm<'
    '6h_z8r^IiwM?62@PGeFHiaBNkVK`Fo>sKARE@+$=Bzr4fbrjw&6eNugLB5N6^I&iZ<mFq#fI&g?0xqv#kr__<9Z8>Fms;+9@$zQQuGR6Ld|kd(n*SLm+p|d1'
    '3kvx!6{A|UF=^gA-{n}r)9$tkOY`$!^IIHUYxrv`1c9H2tD!ZHH6eYoYqP=0W(ae{X)~-ZpAU9obHmfwS5Tn=U*LrGPwrdIZaTMQh$?j8ttH%V&F0r6rSVNw'
    'Btj&K`f2PwDh(JB$y3m@@%U1k^~}jB6za#{MI~<%)9GB}pTFg7XbfzWu@Y4~wXMNy#-Q6M$E!A2S;QU9+*q3z<9QiArEmAYkkJEV3KNY*^`d5(;uF1X<6ZaY'
    '3MH+L`5(aEb8y$-;pQcd#t_q@s&g`M2gAkAx+kmaaQR+x^mNt#N$Z=@eH!rr5+K7`XcatWJ6wV{&MQ~9qi*+b4D+v~GoAE|!q)L}IkRaC!yTYaMcyt*IHVZw'
    '`zxD8-72X#+?t(scx^?}i87?d>W#rzX-V&xg50q_@O(Y*pI~4QGz~c=lheDGmQc1Yqa$U%=uS&^Yw(Kh;Pub#tjN*uybat8VY<!BnuGB6vVR|TYmobP`#s}='
    'Tsqb3SQUb2r=xe@^9k{Q@55aUK$ZDU1sH&)s;wQk4SfJg4|w^WRcg_DdpeNmN!_g`&T@2Dv|iF8aOc$Rj?GXzUI<_gm2P7z!@v)yJMn6O4_NB>?ac}=X>6HK'
    '0p{wO{w?V4Z)W1cx?Q_|C>DYOiSte&`ZC?DJNeU`$&vr%>SX+S>E+hizNUl<_&nucK_49)G!du$6}+xo2G@L8t3c9!Gf@W5qaV;0jN$iA1FQ^o>swj96TUG|'
    'AGYbz(s(#ldUEHOMlSdKSR;g2m$>dj#(alyl(@d%S4+o!SV>^n>J<2G=Y^hDKA_?4T3c6}AonM)b~Ao?_-3I#8d@0QEK0tpY>kJv2=6zYqDlPd*PvcieLsd#'
    'ztzhoOZTujfxX5M3B9SMHQ_HA)h@fyF1{L$W9DA99?VFbzt117>ccxPmS0Uy<?_5E4%+EEY}bxNw~VbwO_sc;E|b4Csr%7EwddcieYH|1a-~3Rb9ME)F&~_C'
    'XlYV`%{#v}7XB5pqoNv%_=J27ReubdO*P|lPDzzlPx+Zrt$wlY*eUDm55JwceYM|0-6`V<+FK@lzcfE~18Dq-3j*>gKO9iCR{S&5#O0~U4b6|z!C#80O{vy3'
    ')6MSquz&*BC<)mQO-uiMdS~$f4YuzZC@9b}>Mr!w;YoIHi^i%~EbEBjo_AQ|=V8zN?<pv)F#)w#`+SAnSjZsq=Q`ZA?|D0mE8KBTs388V_08j@1#amb{N4=)'
    'Nid(5C9P=5_c~HAnM)3=R=-ySY>B-5H4g1Va$hr-tW`fO2VIh%)@K(*O%^q3**oCd=|r;d08NBzy2K!nV6ycto|Hf1r`@=;aXFo5=XVbW=!JD^EPwrciEQjA'
    'TQ>g8(SSMAX0N<4_rS~clx+(U3_yF_gc{A@9rh+&A8TKqdPpt2b7e*pJInJo@5Q-r@9E5)%QE%o2<@go_ka7|WB3;VH#t2I$B$3=GvIBk-q6X66sN-A{_Rwb'
    'Tl~?7*YRB1OmFLM(3;DDx$T!1c4J(2-SFdghq<dA40=!Y^Lsb120u-{4wT8}W(SpJA5G0-G~c!I`H!9kvHSh0_2PA3PY&!~#XXx~EmMSJcSp7T(Ngo-${(mo'
    'J0Sl9Xd=S0?Dy<-70aq`IZ&(@=r8#VPNnv&o7(L{{s|H~LEN-8<ZPCy*wvrB8Q1vv2xy+@ju6k2zZl4+$)M6snc$Wlona5~{Q2EPZ}RUa0!G_Qc1`*1XRI4m'
    '0%p`)HTL;0WO}M*z%xNVd>LYjwR_|5_b|aDz;~Fb-?;hgYO=32=bANIbU(xO6$swf%jWz904?!>S+D7!>~)gtKK0bX(aH4W!6RLu_*tvU20IOC_i@1;dHpC!'
    'UfW~N_7!5^2RNcFGV?v+*cI<tKYn$mKRvOoeCf2DF~I9rs+|VQ^I9FiT{Z?zirtmo52TYPiZo~!BT#~w>W??NPI!W?-+~{Wf>?g+Zedjz*3b0A5{{AUOI<aF'
    'hT!tpVCBm`4E^DZCjP2Y7tWN)1&?euhGuVk&W`I-(U=`~69&)v)aP2XSzV9N`)B+*O6}KiVholY>HZXDvtbbf03m)7Gi{jmR_0!h198u2)`B%)!>pWvqOZGG'
    '=l(hO?M~}?gkiD%b7MCtwWPUZs44yaqe8M7ud69N=wDxX8VvLPtHIXH!)?Q~B`O6Q$QN&9NRv8ugzw?4l^Qo(@XLa$Q<@`ya>YBM%6<mqtDQPr3lp(szH0AQ'
    'Wze7f;-Srg>OygLQ{sBG&feL#eAvXu(S#l>CU;zjJhZHgBk3Uio=d9*__u*6`ejhB3?dF#x+8~d7DWYPtL2J5Y?kHCo0yPR{KP{U)4k@kFP>4Oe1a0qx|!fP'
    'F|x_ri+r90_4#EjjsJF3A9(J&vvgJdm7dA1X;Y1AKots*OVO?2cgk!$+a;exyV0{OG<)^n#;Rj{XY*{RUH@1v+`fvj4!EcDyJZi1=dnA{R-WLzrB+w#)5Q7l'
    '{odzp=UkrH;P&GD=J#B=c=4XptKdT3Ka6$(KOVb1C?E8h?tGqkbZ9qU3LjzDR`Zy2SZnIFsl0($koR3;4%ox~&S}x$tIzIor2^4hBi27+!S(`b@rW;*;q={I'
    'Z-fT1NJh?UkUb%5sAJJV`*0BKY>RY)RFM}SDE^i0RrcSHFI@r@yp6naar8L_+*=XSX)(WLV}<prAr6W>TrY0^_}ZcE;{|xP)LSbRfkPprik6>ezLmerEN$8H'
    'D7rm`NWoMlV`Go#%5Klqoq=N_Cvf?TJxuakq;8>m@#o*=hhJtuy5aFd@n<Fg6B+~Tk2z$u{$v!v`CQ6q;+;#Y0(zfC0(|JVG1E8Vx^fV$T#_Exl8UwcH<~s3'
    'zj~8`pY9YIK(m_Pt<6O$nZ~mfChy^1yV5Z)`?K2^j@4?HsNRp?!AzmzQ24OiovBxjQ1kO$S1`AF6Q$1Nc&Ips1dLQxeRV1?%agDl7*Oyb?w{SJG+XhP9{l*Y'
    'JrR2?iG$C5Psjci*mh`1OJ|ioSnR#qxH_i2;SQ>T%Zuo)FZwnl>)*!-n<K!k*GXnunjbEYUVD@cJ_BI8UZc{;*f$Oht9DkI(iM8-qr;fBC4b+c7QdiBEN~7l'
    '4j#3Jdtu=a{c_d4H!k&R+ip&K70u~i$N5O&Hn7tOA=3di1VrmlXZ{Bj^C!FCA*0Pbty-rAam#-m+q?hJLUR64gEW5PzEwGQwGkBDs_R+79~3Y@Q+dfjpFR2s'
    '_Os2nV=f*G>d4E|-w5_x;0xHX@ecB{W)X@0<`H_#SUwkEy2tH3^fMbO<Cc?SsV^g3hlQ`Gb;_B8b5H4ymX7`oFl^IrFC&a)y;48-f#1j;riwgX%<rB3d~96p'
    ')6tqgHfiuwhY$Ky<-Xu-D(sv0$z{H@{=Z#ykDHJI){o;Vi=xa=SfLkkJuMCTRXWvKdM}?5ePI07)Da4C!f&Qq=zux;khU9Lp;l+2NcW(F{*vJS&Zb}Y`Ivsi'
    '?h2V0W(b0t$&fu2{!zN4C(4p#@{*4x$Tl0WYo&C4H<7)b23dXeUJKWLD~DTl!{E+&vafI=)ub;DcR4=}r8#0APoS#a)j2*-To}B~me+lO<*)+{ZcKN2i$%J+'
    'MC!yxE7v_s+f)ZOXJ{|+$My}wt`_$snfJ_I|JV#`RQrBN?hSGBEmI+^y@e<slAbX`W(_i5ssZeN!QD;mCezwD1+c+<Ppn$E8V6u-zSi&8<K2!f;YVQl^s(cg'
    '*?<$pa5>D&VuSRz!k<GNcYYiH+ws$BXP>nVT|>H+5jYyEcf?&i4~M+NqrX-{C2?z6L~Ht681^0N(xsB-3{smJx55DhcTQTMCNuQJ=gkeay!jc`YZpyw^kzcz'
    'E_%rNFvpY^3e>0QTun6a_Y)HHPs|Uvy%#{Vk%i~w1-_CJ@XM>31}5gJ0<MM$e`%vTU*mqYMy=1(9?JVAP(33etFunkZkFYGx*tPRvptDCO1wPP%Mzpp)n`<+'
    'Hk3~F<H^*cZr1DUZ)!gX8gpG}gqjZcJVBv+#)kYJqO=7*i?DYe8KS_U+3M}%t0&jtXoLT*e_q?z8I9mc90rNh?VNRFx+VA&50_E2b4~k$V>-Ej$ZEgxC<-|K'
    'jZh};PT(3{=7M;q`(OwC)y_-6Nz@zk$1{fw6gG?1V;)bbV^-pfpyK4O^+&qNU`G^R)2>`km*ZSSZtS5uNI&E^YJ1_!>;(S$HNvi`iaN7k28OqvxHDY{{^ik;'
    'X%3b*cX3`?@%FfMr#<o2{1VkxZ}HimhMTr{oA)q(Hw|iC$d@5@fc63~oi*A`kIVID4yj3cRys+a><Tg)OPh`gtv+}(xHh){+>}xsA5H`E4SZ(=bQ|$3ar(hP'
    'SrO^lilUH^(co%QS+@0gHS4Z^j4Wxsz_i<$QM^Zb7Yjiz{|4l72}M6XnyT3^@DD+Hk?H^tzoKAUZl9~x*o<qvEt>zCEXxW|91fma45m02^v?KqYEspN`1H7Z'
    '4x;a=$oHvVd|r-cqw`X#aJw5|9YItJW}moFy#DAdiM}}A`n6z=--zMtg+8sQlxV0HR8GsNk!4!v=gVC7CM|51jSf2zTn)}%!m*F@*|_%A(<4>trfbpnH8(5^'
    's`;$NPHnt<KyTeq?-MHoO>!yJPw=lYQ6;YQFMo3*7r8S-w-~kft=oH_Y*aROw7C4gNoe2ApEeoM!f0N4qlJ*RE|bSKK>MV2Yd~zk8WqWm8(F`yxojTmc6EQM'
    'Zmnc{{VA9v$oT!#U#eSp6Jo^Rj$~U}^xR*qa1w4CMC(=OnEAm3UB85sfp(LzV2^*&0-2+`a`JFGO6UA=VEp^3qk!0uVCD3CVGX?rB=Gk=7NKYLF_$uy9dNZI'
    'eFRp66NR?VezNXTsZyhXOh!`^Q(P`UnvWF;4thH~$;Q~ru;{Tf>P^?fCe&F{x1aTps+ua-G(o7XSZwmWw}9Sc0{Qjt%@qEq=5^rraC+g$+&P!irJubvX%xXS'
    '=yo<@srNn}n>J9jHMv?AcFm6NuQEVak2HeoM*KaTzMV^Ijvo`a)zL+Ydl-6~bD^qssv_(%(nG~+hG4!YF2_fKs+K!4YWvV4x!k(ICA^RPIk7`lUo|$<8i)+P'
    'm+@8W^@62R+e_=5rV{?vWxER|#NC;_qM})4R=GLBtE-Qfx@nYU`kC#wCXIIqhf<oy_6$_I{p>^L%3sQ0^l@HYPrJ+pq}zRdwXcmUD`#Vsr=C2Qqc72Yw*_W0'
    's+}J*KU0C=60VavWmXpFuG8aJR2EJJ^)tTlBMO(-_{GPEvYnC3uCR0J6km{R5qN-D5vpY$|5MV-YA!1{POH1|NZnpmUkLmDx#yJzD#<^N&VA`zE{@{Y(oiE!'
    'GbCbE=s=`GrSeCT4hkhj&e#4vzxM)Adw<tjpEYLoPU$)VX64j8d$?b!D_T?*vs-14HGC->Pxd=*9MDm;RE`J#l<{19luV)Q%c0vKsU*nyp{(|}AXl2plBc!j'
    '5xz*<eR)wCm>0%lLc?}@@u!lNrI9|g$EkqZV_`)-3e|pK^24suOD*bMR6NmREd9c7wlXpQ=CYo+Qy|Qf*0ilG?dJ4qNDH{Etodbspu42?w=id>x;2dgaMkXk'
    '7M_bc9+`{dNSZR;D%lbr>Z|udk&K9G*4it%4W67~KRYI~jWUco&)aENtrAR`S1z^TLj3g{M{JEoW*IP1=XvSfhCcQSb-2J)W<58AzlJ#nIv^GzXJs}M@qzMK'
    'lFHb&FyM5U>^t$PnDbe5emkvn$M&Zqc=8+6E&6&x-6AWv-~cY}?Llw#;I`z>{)~rGI>YYhe95S24PvZ}M0j+(b0@xsI_OUgMuYyCHFY7kY092%Zy?%C4h=px'
    'eDB7+{7vaY@r#A_SJ;9-EH`;Ai<uxLl-Jnc_leuDL=rxE&5`r%&#9jat#KSX-0s%%%9pWU7yYo>@Ar<i!O0hC^VJUK5XZM0d3{((Ps$CRX|H@E7R@WlJ{~>q'
    '0CE2N63HX!W9{lg4?z8yRZQvYDEMJ!%FwG-?PGe<G2xC)zZ^n&7OTm&a$58eGu*Vpn*8OMW>LW=<@?<-Dugt={ZP!-qFOV3Ti-2btz0ljt2c9Do;Lv3JcCp$'
    'y_l@YH{(jk$d?~+hCzut>_A?Xlr!<pXLhw&qne2luScuDr@IJuD}AEpP!Y_%h2toQOn}v;_1P&H8CDPqX#!W`dSY>i`PHph-$zK@lCDW-hI#2~P>u_&E^c#f'
    'mpSuED2)Hwkr~uzw2z*5y{^ujqGnEt``4Z6zwOFs{r@34B-J@hZK8v&hcvS~@3WX3!@~OSt7e?qr_Xze4>|?ty~gCGwG}^!!Ytd>UDjZFt4ZTLJ#A1dY7MPU'
    '7JFoRM|b8P&#sFi$KK1$WAuK$I=Onv-RIfeT%sCiuog5|6GMZu_i)N7vokng^K8K&?3Zxr269GfOXO{20|t%#F0rf_^${y~fH!&IA-xLhrE_ukgvhvuw2<+V'
    'Bu?8$m@GSR9wlbJ_PczBqoVN68TpVH2_Ql!KBfKQ*3lkRL3U3%`_kia#o5!s&e%<);;@vD#E{aRPYPcjC&}A_J)wRVUSp>9ilqfT4)OSAVV!MXiRL=As7oSX'
    '6q>trnw|A4HzjN|Cj$8T&6Le+<~-0-fghnG4OYU@c^eY*NB3=xxy&Y|u^}}V=~r{dm2VEB?$k5K`f}NSKrQst60YBdhQNu@RP;Y5*AE{rVTZdv;%qOUUfZwl'
    'cFA6LlvQ;$tpUU{rEZKc-}a7~%p$qcDBV_loNt_Cjd}P4|Jr~KeCajYl?<QunxG=`1Mbm);<)#l1d5AO(RJnOXazdV9e((;Vy-do<m`?8D@Q2bufy@(-~D9>'
    'H6oFCHZ#qkKmflisg-E;*@N!K*t@JbiED7H#|sQMF-SXfd4el8J80d<K3!k+ucAnfS39u}Yw?<5aZ3E`CVzp-_>;$NT&eWeO(Z7!&5ayQ<(Z9PP3zyaK0B*B'
    'bNkj^!G<bht=m~89TIkBmccjw7)~~L{H(59AMh!)c1kaj{WB`U?%<b)^Ba}+E{idUnG}C{Rz?`2?3;g(8Z7MBb(ii+kOJ}bQ3RlM#n#oRfST9_<-9gBMg;rn'
    'W7q9a(P`%bPG^<lb-b-)SbJ&?<+;8m=CjKoUA_A+a`yS)_iPVLR#;ZWo6m+x5J@wiI$vn!Z%92KY<IOYl^<UI_{JpL6~Dphn$2|D*&g?j;4Ty^(y24D{>NFL'
    '^<@c+X`xe;qfpW9Lvs_S4*<J-_0v!3?lEKzyW_(hi=s|<hU_P~w;K}qak)904nk(qEaYW)W#44K@1DP{hpPiEUQT#<5<rt8NF9-3V8Lkb4sEW@TAi8#QR2<e'
    'MW@qYn9epp_0^4A&M&7v@9VfMV@-cty>nPguCLV5bYM4B;)fQ4KxBOG`0|Z|a~-qpZGUIcKF}D`-k?!80Bp)h@k^~OiB0=fn^fcVMx1!=xb9<V8m%9RS*_>C'
    'U#owDv_)&Kw~KvHJ)VZUGpCxdcDq!eZ?Ie-VH+^JpQYLBygCO+kRou=ivQZ>Ws!HmH$|SJsq2ekyQ+D-^Pc;gxmdGQ{j~eGms%bY)#sOkk=Nz$y^_(z&&*%_'
    ')loyOai^R!ThcW?A7-b?XD)pjzt(`E@9C-cm>=zH@M-61b5Z$&`|Z*C0gya|ilDL-vQavy)zh)?gPP0RF9=@iNXCmEP@^ZcNoU{MSnsR7$(cG_tjfh?B7Fyq'
    '=)4oNDc5>H+9%<xd<LFH`F;prf2B9M50oxIfyT6&uv?3*%=g2g;|d?&FyIg0sZWMNd0<zP0y<ZSrYV#}%-@pD%F&KXFk{y;@cKG$E5L1R&^>$b#<W<DifJ$E'
    'illyAK9jw^eiHSmyy;M3E1{&)c|uQaO+P8lnJnx#urAzofWFKv)sAh>JAu&EkH(#vRv8ogjXz%luvgtNtLtkxKW)uewpQBTv%)}H-7BYlPqfkV>ypab))jBR'
    'vY`PcAAL1NU%aaYEI4{C`~3bG{TfeQBPZ0ka`7FyiL>ffCbOWcLLE1HI1{a*Rxv#$w~yoJ)&_5?M<m^`D$cRD>CWALtv#!;qMc_;ebV>Q+AwXCU}pyIw~yAR'
    'r+u}<eGS|;3^b<(!w1Q@^}i|E#lHVAySP;cFk;n5u>7*do8?8GkG*d-64}VvED&qqQAitNd!(JCNgwdHx7nwwx!mBGI^;X<-eD%<T6+#kM~eHboIcC#UtP6c'
    'U;8)rI?sWq+>wWKgbn@AO@gEwDHXBvLd^RYo8{5PI$vGlWp_{ed`9H+-O$fsoE*f>{IFZTSr}tk5ngUeHhKD-gh|^b+PN$H{1mF~z}F=)?h})5ZOgSRObVZ)'
    '!#h8ZMtCt9sw<d}>^AGI+(}HJH4D_a$tJKlcW0kicsHqR8>a*2%<ueznYOr=%8n139`@gICnBu-o6?8FPm#T>-dxzx;)tr&0%@T7`*t{<e5=zIAf|TPi4+Dy'
    'sw!+T&HPPs%o|O6m|8#8wwqd~)=SWLaD#Xc^8=W6z<I_$5BuJ&u^dOw<>f77E4sVKyL3fdbd=}c$JZz7DCV=nFnlZijx(wY?sR`w1I;Udt=cT18#UKSUZPB)'
    'itKg-R=nqtnRC}F68Y5JSs7&l059tEL`ZrzuGkU_Ny4m`O3%h}*aKPZ_4aINzS$aX$y%}2U9y+50gaoiIZ(t2j?7ndz}TpV(}enxq0y4YwdcirZF<6PxV;Z6'
    'pBxfMffvouTdiH~@JCa!_&$y5E{x)4=g>0gUr{cWdz;^h<CQKv!9TV_UZd@5Fq1Y@UHG<B8Yth-$#cVX!>c~qft}5Ai?nzam{*Nj756{C=bDtJRQzm>l48bN'
    'jN?j~eMn`2RO=YMXf=##&u4zjS(w$hH?&p8y1Z(gwAs)9^yS{AzBq$5Z(FHFWT^!suUHrBo3SUm@2BKT*TI<Oi}5^=b^ew7Zsrr1@QnT3J+1yytSu+;?#8wc'
    'ou^=F0Xdm|E<~QCf=MD$x7KseQOQR5B70P<UBVs6?`(jf)v})K`&@Ed`0*wc&*kWO4&ekbl1sco&;4k78kqOA-khrUVTp;6QDy_mQfvD_quSBpR(-#iN;b(>'
    'C`MN7PqjAN>YYhJq;QM7PgG@KSP60H3xA*@^{9+&I!oeUt47%<V@Is;>x{dJSi5#x9CEn~H(oZ~3S?{47qfEl-1c&MH`ogB+8W=>#Q?_RK-DGvq3KgL-AjEr'
    '3WsRi4ubxEr&d?YrPYFu{SX*80*JadxA&d09HAeQAM%%)4EyxvwNO7wmOd_3YG`lo^2cSXz4H)B=u?zBgK}M2-1fgEh-!3I?L$e5bVqpe)F*)+6Y}S@TdPh$'
    'Ytd)#k1XJER*4K3Kf8QJJxHtGUU`vxpJa$VzjD^EDQ${A5FHvx-d^G3+G=eQT^Bv9X)8D{r^kLp)uFQW%O@P>*X8_J-b<0|;fnd3_9iG^J)O2vr!%`V4ejYy'
    'U3wK|4MeTV*DSs@*EcXPrjKm9t;o=oUyQHg6VINE^{y!(leb^3ylq9sf72DtTrg|`oVg1>AGb=36xZ9;?+35fs~^3CkC+Wn*YIx->e{N5U{dXvtYun-`S$V4'
    '<P{J(<m~VSlC^0(Y^$pz6!>|QKYr`S$e}go(mai*c5ibrhO_l)CF#kE7|qJ<#(Va?t^J+x+U=<<ovOQA_Tpwc=f{tmt!)@i7}gz!0ePPY?Ec6-aK>-?b6aNR'
    '*5CWkyyxXzR~j8R^=zBaw2VV-Yf!3(VtwZ7G*knSfifv><a1al{QT>Q3b^h@MmxKw{ot>CzIk%-pr>N18G9S*`l8$ia<#E%$KEdJpxWNwW;qug^5^rId19xJ'
    'Vb`dkY3-#oS<6WDo2FIK-i;2w^Kp;KLt5YA{><Ea!ib)mD~h{PcH{T%-ZSS6$q%yJOr4b?G(K+52$z;}<ni@=k8PF{X6ND+pt%|y0j_%CH(RYP-$pT^QRYka'
    'QiYNlH_=&6XN^w^$e1=xp(uiy(@wXBG#~ce*C%#AYXHyFG<uZ|IUPskv9aIw%jK<J0ZzxuYGq&-FP=>4N@FxTqhr1@a0MTzdk)76gQ?2VA4WNzC+|3>+bw18'
    'hfKS|^2}*9y`8>>+)r@fu8nW6_t!SYVp~1;xooE|4n4opvuyEO5yxFQexA!){}sx5P&>-w3@z~4=C|&ZhSTq#dh}zYmIE7aS+b8{lP_@JGDE^_+Y!vX!r<9e'
    'qLj^hjT~8W%ZrdT&m~Zj(+*cZc}%04W>$m$bLXwrr~LL64D=^k3c$YV<2&nZ!fJ*2Qk{(HLWNf}9;eADx=dx>?Jm^g`t)eFpVvM7mgdES)va5s&KXV82P508'
    'rKYB|&gRC8&+r8=M|G`+PewRy@6*PZTtc@te2efh2BkaPsWC0J)vbS)*TsoskWiLKs!wc2KwVgMQ!0>jQ~Eqkv-_zj)V(G3z*RQok3iO<#mrvvi=*@IusexC'
    'pQp)Ls;eJiUNLLBJZ(HY9HTDQhQsykE!cH0352y+it@#_jjjSbWf#luZ{KhP^~JJ!rGHX*kp=0*nS&Wx6@PNxDh}-Q_}HI6u%qB%O?Ld2d%z31D37b(RoR**'
    'bg063wckhEu14Bpsf@bwci?d9uW;>MOIi)B)8Fs3)=w%VMo;}SxvZOND-G;x*tmYe-btA!FFCj=19o+nTrs+6k}wc})t>7PUlsh)>4U4oe$XnnU)Oc_)gsA$'
    'cNSvbR7vH_?)0@9_V8y59+vl{-xEk<06hqjjME9--uUZ>Aq_SBK5Ym1x$1!R+6|-jzlO)BbN%u+Ib^$@@tsZxY7f1yGt0lGNAvpVcG&h7yfS(E%fqhm(|a&5'
    '#Us59?*8JbiR=x}0DJ2`pJAE3)obQKG^;%dwPwu;`{+H-3#qyKqsXB$CT4?o0<llLDjzmRMG|{Q;$ExiD*%4ttKkGJbN{*Y=B>6)?u3$*)aUbdT!8TtCDL_m'
    'ir!D7{qi@JA1q?j4$t3eR5^yP7WVF)fSdir?`t}K&-EZ6R@}73KbP8PQd_)azt`$xQJ6fx?_n7|rpOt89MrT6aJ*;p(4Y#oWKG{mYhgZ0+p0mV!`X4agleNw'
    'w=!=rn;WYFBqf%q(#8iGSUR1kivuK!Z4vM~Vs*Lc5N)*zKwP`oJ~a=n2QlFJ_8gjx00E|A8@trhqS_e5&xY}!%wt2if4sANowvPswBOus?+?b!Cy17yjSoXk'
    '$m;H50aOkt3clNE6b11hqn~T7pZ7>Q;qdUfx`rUum}TX;O+TCCr{(oMxuZ=zze6ocdfgvZH;=Ys!>`bpL5a5(@2et#vpXk?i=av`vHUT6-JtD)A5=P=aqxP<'
    '^C7b*`ftVhl^VW+*c%Jz2mWaXM@20`>?U@WXN7{}!M8s?Rj&;#8`S&Z(4~YvDyM$h5TUd5m^Q(l39%4&PYrou>@I6EAod$;y=sh~uum;o_0t{no(<~PBkE!2'
    'c}Uu`{iN)8hfsNefm|ITm*NdXW}ASPbx$rXE^kkN=eNkxKW{4e(Gk55N0X8py{`*zal3%4v%2j9Wi=<RdqC#6$xk*PU{rMabcIA3W46aO_A$MdRu=*Rk}276'
    'plQc<EI|R2THM3^dF;Hu_f5qH*B7`}rn_3$P<Rg}6zfs^(VLI0(;ffD!>P^kdjEJB4Zz{<-V3Ci_hO`bL;16UVVXR+BNI)q-fwt+ybjxL?IaWyKU^L4_X;8h'
    'r3EIM*ZUqs?Tn}mgLXnvANTu&eQMak?(qH|8l=JzKH=f%+&&*B-e1YJnp6sq_}R8{wK9X%3GI!imcQ6^YY&uo1Zib00jQT|0hkWtRBted1<!)XkLV_M%LCl9'
    '1u4`8aqSX+ibvMPxuY}x0n`2(xEgUQ+HUT(-}-j!2PUb?C2`dGk$w0zHRjRnSH}@k35Tcl!}Wkaj_%J|b<*jRlY{ZD9K7GoxbSqp=+uZhoZYe{UQjPrj_Uhs'
    'rE*p^Ro7SJn(#V5&P`wm?M-$kRH_>!k*}E0^;riE+|~KM{>>C=@U^$^TKpir^#<R%IokcMC!|%{zSy&x2o-hfck%%%Z2{Y6uT#6+{a`W~<REfeUv55cZJLt-'
    'b;*@l+pT!cYiH2gs16^K4%N)r`rKj}A6H3r&%o|8!|`i4pKOqeODLOdyHCF0`S}GJY=5~%hChtHagTX(GaILSrK(Wz4&@ecPd=SMl0McEp(oY(4PT~6oxE=D'
    'yL%<Tot4F3$<6#C!f;q#8da>!ZrYk@JdbFKH!Jlzf2>Gk*TC&ZLJ5D-D~|1F?PpFZZi~M7^Y1hXZxHzXG@B^<T^>=F&a=x9TkczjYMvc6XEv{55y+Q7+|tgK'
    '!)^;0>vSgGnIl)-HIOEya*_cH^wq+%bEYki0}{pK3tg*1>*t!axo%zh0zK%vpDE6808}OjEWUdTSN-!t)sS8@Jl%(xD;+84&0^XQ0X#nZBtp!+GFxS8BkNP+'
    'Rj|(1&DM?b)UeeMOX`JGb)93HpM7}@6X`G6*cbcST&$*Mkljk3KlfQo83SXt{F%uV9bYGqv|=9Ro#_6a`{a5lT45#IJyd+MIMc;!BoC`>mi-l+?><fjhtae{'
    'Uc65<=BvYX4S7A*vlpj=@2{`lYP;)>`OfFH&eZm%R0OVpaeaF&@^CZ&BBbrAe`>P_w3>fs+$SGA22TA=A;J8Es6&DIPT=DboVQ+_W@A6D89C*C2jsESmr_?u'
    'Dr$J0_H&4Z(<3E1p_kW>#boZPhee@urXn!?<HqInrs16PrqGjSGwk*L9U}X>+Sj&km~n|1wLhhe-@@gIV%Ahc4jHjGs@C<c=|&|67pFF6?(J7|eRu9~V{Zl%'
    'rtH}hSHYHF^fEo3u8CNas!UtAx97CB`=f58Bu<WVEY|(9PZIC2IV*=Z>B#JLMGXCDs}Fp;tMRWp0;y2<l<@GnZKY)_HIX|OzV&6Z=S_?KV|yP=Z(T}$%z#~S'
    '#v=HSl!Yi6C(}!htUknFKCtZp>fIEwA%m;qwOz!<ZTNU-gF&5*Ye%uVT4MJ^uMGgk2{@_M8!vOosq;@Dho`>x86Ni9X)y0{tG7z*0CH1XCz~cPa6a=7>h!hX'
    'SqJ6a_Ijw$YcNVS)|~N(d%I9HUKkTXmgr#`%Z@3{^vBbbrVB63^}nX&LSdsXo0V!NS&IwHft8=OE|d?8fF9pjN_%l8cRwW-4Ypjxo)3v?i#TG@=zaFSm9}(h'
    '-!|KQV62|I>wUDfYtOxI$=!D1XRW*k$A86p;2oVw+?n}eeJ>5EFOF1~((gF3#66S3h1oNUZVzaJlaUt)Lz|vmxMvidwdwFcO_$F@WMIu?YE(OZm78Fv!@E;U'
    ')JGbwsM`0Uk7hk}1T|ib^kD;fR<8-d76radS7KU^9@VqmseI<S1jOYhM-`)OSP{unC)3tRdZ~~0{r-Sw-@@Z_9uw_B75}W_?h80fj;}>`rv^9Sc|O6G0Y1|D'
    'U(G?TZ_E`T?O;!{bU31E1CP{CtvB)CJEXqfTF;;tl=4WQnbc0*&YmcSO#T@A(ln#)--}Iol$q6qjbz@p*hd2&H56GyHWl5?=mmiA;ZghnBYl)!F*FH`@w~H6'
    'Mla_3R*@^!&<DnE7o#|LYRQxCHzvZVhDzF|QG3)ThVduHIa7BM;YyHa(BB<sq?YJn6Qzd6QzlEP3=U7?Knv_)Nq#%Kb3k_9y-9@6F89Ym>wP-KK(_k`bh%%l'
    '@mv{XDL~J`sM|jjZ+cO6QnlBDoYEjFnKOC_@(=8wGX@DJmj8vKZ(*KxM+!Lzlb9El!`)=kjy?w`f58PeM%HLVx7@qVn4gEmVD9o0O@R+PL#=UJs4S<|{n_u6'
    'e*1Hqs<-F!+FZs-+Eh_rB@cxR^e&dNv)#{MMM0^wezTy#c)DoRmbcu9o$P7+qHzey+S$}y?eh4l-R=JJ^7-k6|M;JS{tC<RrK+!$>JY(@S=U^{I`tk=Z3;tY'
    'b+B^whw<T(4UZ4&4<DqN^10Tf-Je2Qo&9?6y7$%`or6fPC{VdsnfC7c8au7;24=XFffd=GtVpt>_asNw=FV(P6eGuFLXO>dTqKD*kj^Tc-`-#Y3ATE-tvS2u'
    '_U=Orjo)^+0xsbfB^ubteJL4Z<uH5fFZR$R(aIJw(<o@U_<LjRnGE+Dl5VETol9fyI?1TthBHpY0oi_{Gky%~o&`6Se;D3LMtY@=u24|DU3v$3fV}bJU5ZF!'
    'Ve#I;qN{Tl>khPLklkjwrMaJdmAIdcCg=gw4m7V2qu+Y1`XL-QEo(j-^BXE_exJs7I-MNdDV$)EioB~o2FkiT6kUKDJPL?marUgyjk*ovswzT{PkZ(L@ln2h'
    'h?=j|gkq2``L4L9?&Nj)yOq6;D<B7dm&t|l{;HDv>HuL>);@ScWN7)jGoF{ux*{p>E!$Eq{-@|nb5u{`aK(3S@hGG9ZjzTTn4{RJoQ-C>am~u3X#3UX*dMeO'
    'o&;5fslBmUmT@{NDg4cnG<Ch@Hb&x6D{h>c!H2I@@BJ#ur(X<c%p`vDkf;tyzlzrLukz)ZDrn%ES`{bXtn=ovGm18E(%3@h#$#q7Y%jTQ6ei+X&kzf3Jr;hQ'
    'NnVC@GG88WpfW-_oBCiEc!ve8ug<OJO4(UB&^vAxr7=|&1N^USy^riUSC$!i3+dfoH~WFNa0X;uiKj(R6-i>qWY;+A#__a1$^x{z@6U!X`ii*w)Ogwn*Ixkd'
    'o7DUqfc=JRj99ZwJ5#(noxKOScqz_hEAvjberI5&lieUPo&wd#lgaweQ6E`Kxf1<(^f5B&cYnH409fOf3>7ydpr}B)?_Oj2x)V>e$!E1^Y4-$2@T~L;G{9Wi'
    'NWu|BcA5bDE2C(&#Km$0Nu~nm1ExIEo!j3;Joj^Fe0(OE(W_}rGgF4@zD|J|vw=3SYZ+>HGd~a$1Q4eGAE|={!nRc<F=O-Z>Q!fNpzBrVbg12b<+Dl1mp)p5'
    'b75HOc;$wG#vQ!)1j@qg9KJo;&(Vq_=FA<dJxt2_X~k?R-Qy|vXkU5F3AN|NYA@E)d*usJ@l9?U<eHp++Otdv+wz8pJ1u&PS0?7_qSM<|O7$cmZMYB$dJX;6'
    'oD9*$*<E7p^UwD6#mBq8@0-WkT*g1&V;Wo}&f3Fw8})_1bn2j==18b_7URDiY(DePchqY5zx#s#omKnwobKRTWmpVbTRGo+lMX1h+unC@aOf70r!NwS)va&t'
    '<i>a~lI!T1_`JWwL*7xfYd~DPtyKw1q|k0tV7c~A?R@X-rK~=w)lV_(x`<?L%<pTFFN0yz?L7zA;mJ9N#k)FF0y{iapLbmsme)#b<1ccgl=+D<F4KVGwQAfx'
    '6ifG|iTZ3&1t=DSQok#Id9sS;<N#XPmpu*@+jAmyEChW#SYhc3K)YOHSmJ!=7(7ag0d%t5m1b4iw@34F+IDsi&Km=~T+krfbv7_gK6=D9IQ;%uRAY+K%T7t&'
    ';ED{5n2c2zF?{;#=ykPgmvL=YbE}K1^xTzqZW-LAse808W~fE;*TmjZX{D1Hj#=z_?rN0uT>C)u$DJena`i@Q@%4fYeN|i6Gue`{{aQ^BcV4^A_S9CdN@Y`^'
    '-zSvJ*$=fT-x>UHTIX40I|EI&yYIf)Kc>g=dOoFIoBKS=yzhIpIgR@h3AldMcTjBUXX>u(>E&aW?$M<xJHy;B6#!PM%l8-=lzBN=x5P8ICnwG`xsJzuVBf5F'
    'mttxvJ=uV&;S#NuFRcuWHMXTbp(gS8>D1x5zZH`N&aKektFIk=oNL6aQLD~knm6#rR$<KGT=9;ji0!SEYi9z!fzSIR_IP_sP>5Si=6-CFo1VUkgXT}F2|L*l'
    'f=RtEUWg0&9#~uwwZb5Y*OXzz1Z2=Fw3eBzZKwhx)PdNw85|0xdXUbT^=a%XED^3dC#$;9b_fDi7BqLW=EY~zrzYnER4IB?9O#UYH419GbkEPeFm0TuHZyK2'
    'T5&1<)KUAKF?Og|&HF)ZBav_fwu6^tEtm#hcUPW}RJCV2QHn0_z=$%%ex_<8qx^fj9f|mQ+_BG4@E5HEQ>`QmT3SHPjLy?wdLgv^FUqD~*li5Sl7RjaO9^WF'
    'mQ7e?V^91Fv8rx_REK*X^XWrHWxM#!r$ap}-(FQHnI*bFAaOLG;{c`=$YV>-J`ZZh+||o!3cEvZT~V<>X7Ke+Ebz5IewEPR&D-~SK^cHG8j$k_(Tga7&w~fD'
    'zVN3LGT>{yPnZ_>f_NOaQavxNeBQ-|9C{`zMz-6(%g$x~18H=A`8W9Aw8AoC=Qvl}L6mitCr!vSl{c^BP*8Lw2|`SKN(S<01lL|0{M4hB<R;Y6Y1N;Ka8jBm'
    '(X)X^eg2>-PnjzbNv97u2*D-NSZ=x*@;=)>z<YK1O}5*HCPag2yDqIe;6XFj>)BsB=Bnqh>MR<#iC31v$f-5OA$UKrz^-HQgYF1>0+sJd=@JQ6ugj==UsUF~'
    'rPdE}vrYoGDc_FLyt^6Hu=)t&1l&~D;0<dP)u0NRrNP_LLs+wJlHWSL3p}Yk+v$?7#hdVu_zm;%Hj)XWB6mmv(`O(~Di@k0kZ#Y9tmtsVW_~!sWZezEuc_Km'
    'wUzWqnOOtaTA2t96|C?3OVAm9i3~gUHemSh3?ut|vs*<ODQkPUjCKaN@KD3AK3h2^*b_jjJ)Y?ZX`8V=t@+(7)#{^3X*bL+<QMzQUh6jufWMWWH?&s5CcX1r'
    'rlr$6-3!+>RS#`-Y+%2;T5nH#$!%e#$GP{=n~<LTc~(_k|MUeNr-O#v3Kq?s%3jOXq^jrR4br8ngof$2+rJa{wp<>^8#P9FczWprU32&`<||Uee_Ll<FQC_%'
    ')cJHUGP$!Dba<o$uuU=@j@N#(C%s;a?9rI;yUDeM&K~PmFFGto7b$Ps@RoTfmMr|Pn>^;;R?#Kwbg;qwunN3~Sjb&`|Kpy>J$4fE;5L`(3h_-A!LFmd?vKaa'
    'PtX2HZmDyB_zYsp56Bi4nBPz3E<U5Tv!21mf<Zy4cZG#Mf_ov~Hi9|i@UMRNWh$c?w;dcHpgRnyC9<BpT@b7q2>?#7i#=g@L(tErVe5B4xBfyE^9Ll*+1UM('
    'v{r@iT-xW^wUX{2cRZ$c^jq4dhvBZlKCmECfKAMZ%{t4UT6gHJ(Aq>=Rg&4sE^j}p+_3><Qo!1;EquRio}Sxy*x5svjCKd>rH5R|_MujB!t0;WjM?J7yz8xM'
    'df#yrAX>VJ#8n9Sv(xJ5JJ=gvdn~m+ErX`&qe#BlmfzI~;1%tN9!_)yY~Cj1@Je<2%U^#QWCMOTyBntoN_MZ40o>Uq$I)Jr=E*A$lrI%Q>t9q1f4HNYS@SPc'
    'x_cRq-F2Ju_duQ6Ho{r6v{crtTl4pP1}&?`x-i@pSzbKRr`jTMuPi4{aOr4`DK0Ogn-{x6M4NHO)Zg&kNvCydR|jM39#SW=RPJQhoKs&rs`tj@;nY2Qhqz7_'
    'V>Y=|6{S!f_BWe6zzZ?oMhi<Df!*r#ebL~0w)JdwwLKLbK{N=ETE#u<ciR72n_7iSH#b#8sWm>GKxebMyfW0-jT)1Na1va_D$H4AsM?w-YV`xbgVoN1-m~?F'
    '8~C3Wv7unfCgefSn(h`>kyg$AeBlymyC{XuF|fL;q_uDL;(8}Ly}ijorBB}CyDF%e&@WNrmJnNnqO9s^aF$;C75GA)li@=#yb-^Nto+vA0b66;K3vLyoY>QV'
    'DGwHM^yd4Al#1V2Y+%<eI`4|pL%(QR+~!BWM(fsUuO5D|1o(64eL-#u$F8?{^w)I;o%*D;<&&j*apnd?)oF!o?DtJ%r8AY^Ynw_p{<)ppZ}{nKb<b!r=r`)n'
    '38g&zE4@jsixX4&(9wd<^dSZY934)^H?Bu#?*3`K$;OLmE)X4v2a26Svv&V?P);L*te%)bG(d5(Mdq!#4Nk^QwxhcIpDHOcKeU{-BM7{h{|;K`p^cP9FTSJ8'
    'w2Gr5$M{T1^<?!q|50=c4USb~y639zO8*)#AXTK>cjcEyPodksS?W;&>!{y-NieYSDkBm5lqd)GqoLPpLuh{nCh;pG$^LlBH`-NTRvd^^Q)<e}r@F|%llDEK'
    ';h?XA@N;$v6=={~QiBhp3g-oS-{JKO(SVujayBA#s}B$CXAoGh=9Mdb;W5&4!QShg)dl6h%YjoRP-NeJ3(}?KLCo7c>SK%q{)`tC+#O~et`4>+*vow~Mbi}='
    'cDHkcS+I;J+&M}aiNpCpnKW{sR%?VY<@zV&VRzi3S~kWng<>;~T+ZG5(%9VIWiV3YhffgnE~oO6&eY+!Ndn$=3v3JyEHe6R#;bSMu`V~T(s$#sk<Zw%SZsJ<'
    'H0s}(m_rKWI_L=4m&;E&xSW`PiB5s8AU4@uS<X8QF7UAV6Q)Yt8#wgfSIHaEkDpCW7oXm=@$M0<1W@M*`W7Peyv}df7Nl@)`DZL!L)>>EN#pQ4-1C%C;q9(5'
    '$qveaJe+1hP=UC^h3?aZY|6Q#cB%IjW!vqyv&YE~)a$g%{!3|<NpP*411J1AN*`O5s^jhE$Cn9o$MW0h6Ite)ifjj`KlrD@r?@y|_hPqmpT|Dw&4RSq7+Mh$'
    '-$!h$k|PsmYMhZgKW1e=_bX&}|7kw^gDUZHw^|e6ShJRq;J52Re@+{;O2gS!y^dk{p;yoTuFH$ejOo;7!*WV^tZeH1L(Pbyr+UKWvKr1Jy(V#NVC4%ox;9H;'
    'n5n&kQM*C6;_eCZ0BgL?cfbwCZpC=a<EN9GuVpofP=Ia#W(9px-t?U0Pe*AV#dEH10B$FUn}jC2wOfJ!x1M@NpeVK*`Wjf5c343+MUOd0inG5C^W`=g>WQmy'
    'hfI(R|EzU3;rlBdUi~*f4H|tk`U`FfQG&nfPs<N%2uI2lm&)TbG75iZ!^}?{kt|`{D_v`HWJQgb<l^WdHtjy7eBX;P)o31$p7?l&`=_EgM~wa)jA(yGhZh!E'
    'JP*cqm`2e4{qBnG*W>eU55gih!uE$aR0p~Y!rkK?nNE#lB=4`&J6uJaLAKM8xTuMghSTBoQi`?bu7#+b-dJayp$~U%>>pqp|5BZJrSsRP=UQjmg}b9*k8}=^'
    '_IZok?eUz^m8LVv+f4VpY(>vgo9S=cA!zkq6V_y1ml5*`B!6H+%tHCP7~Pg#BDyV5?&Q=33U+0sUaj5;x_?_?vCQMpHCfCX_r}@-2idov<x_Wn*BhGil4(~v'
    'Dz^@5`sS_rL>4=O02O;Uoo2FrT=Jj32^zo#{`8>y`guWa?N3IyQQwp4JkSQpaje2<1g<}ttfmMtW1pTr=$SOymCNTUEGO{FYEO8$%0S%2`F@%DcLguV4hAFp'
    'piu5nAkO;j#bq72qdf#a-o@FbJ2Hg}%A+<JmI1p{DQ<OhRC3U~cREdkhO$F=o4;xOTul3}ucKy^SSG&#*JFvk)+_H1aRudN{;>`QnEzpW_UCbGLxEcTS!29#'
    '_IAR71T?wR$NG<(=j+AhJ*vqW6$1zCNG+XQq2`djnA?NBj<w}hW&DEnKa!grN%ht4Or76o_U>&}bezk_mRKBP+q&w~=9pB2Z>+7YV6kYYBd#mVuz}aT%IttR'
    'ap>v*cNn63s)6~OiIIB``E9)R@-jMh*Z0=onciQ>F}R!#gHMf(-sIl7ftPN&s)f0N-gxKwGWG(gI6OeZ13symoS=q_2o34;0p4;Q)q$i1a|f2%m+t4L{L7WY'
    'DPCc9D;_vCP{fjMqP7}SFY@~U4prS=`#AFU25KK72fZxLPn{;{hE?6qx59nNR#u(;-ny=y>x$8Mal36%TQ=AIsWU#k_tnt_!mWADzigBp6hFu7xC5P!=3+a0'
    'hBeEr@s<hyVP*yAuT7UY@Zz}}HXF;nZXLWNSMc8WFCiBD7r$q^h{@b0-``0Lf{)W#JkA{5r~%K3vLf2Gbe~PA5tP9B<lsAhY7NIiMw8so;o}GtG!16^Q{Iu7'
    'Rx4Bh4?7QBdw#nJ(d6zepZX{kyF+3b)OXMwL6HKQ`@p)5eJzCJ+-bg08SnNyf9O$u6lPl&7}}!JfIr#zJ99Tr(+MKn=`9yQc@&N@t^wkNUpPMwjJNkqr$)fr'
    '+H=TgeAhV*@clYa5TuJ}^zY7TpH_Y=VSIa}@PpJl!*R>#XG{+Xm&3Vz{h{U>LEgG`wobF-tvw-Hm)Q&p=6q15kHOsb(h3+$f^2_UGfTX;WCqn@xY{#)9+t3^'
    'XO3=quM41u+O(4_X1~*HgM9n+H#YCV(gU~7b>v?cNJ`GTH*KrrND*~+tPHFeUV5G(((;gT-l2ym4Z)Z=KYvlnKsNMusTo`4ygAiR2;azlvasPpT3ktEzV|kf'
    '_hR!C7|m%-Hs(qx>11ek#w%_8;*kBJ6|0@pLVGnEJ1ki}SftGi1aB5z%a6x;$Ex}}{d-P~-tyF|_IuZIu_k(k$iHtMyi89UADnKws|^{Lo4CJ87S|8_9%xf}'
    'qe`3f$m{HFJBy+khi<q5&m1M-Z=3Y&V*ipw<D3`gupv$qdsq38;)De`q9(OdbK&qK{$9-J+vUmFtzvHz3X(TgTZ2zy;cFJ{*PjmO(YV_?97g!C;&K$}`F_6d'
    't5#GxU5+J1KA8UPERJ2BPuG!Gskl2O!=dFKRg4raMNiikHG*1Qm;Y{5#8&6GWR+se*5|!Zm-}p&kT1FIVu32nl~a+f%aFLsGuuqB`ikSwhf*K(>O{qwIvkYV'
    'O>bQ3Yb`~8^wD*_YBk@24lVuoqCI%`GSxf({wa^1H7TQ!kZd-2%$P17KCZQ9#1em>q6Tw+wM&WGNS%4woXZ!^EY=ibT~2$?XENYADE_*6dtJ63=RFmspT(KM'
    '?IjqGuASF*?iT%ghuCW80t2-Na;5w2Bm7#gKO@W*ADd7Ilk9}$9&B3mZnh>L<@F}HL$8ujz0w~Y>LrE1vq9D9%h2W!^R?beux+KwE;oVTpE%l`BBFo7&I?GR'
    '=+oqw9)8b-|MUBs3O8=M^&zxRJ1(zvw=qG4pL9}cGOP}wgo@L2?<&Aaof-vx#UWvmwX>csz=ut%rL?6<J;#ec9Om1y5%ufVhY0T874gNpSpn1Lci7d2+<}e8'
    '@Ee2Y2#{^oY<0x@qb5<=JH%ic1N5+?Tf%%1590<#r`2L#C(e3k9geDb*-~aIPY$!z=Kk@Q)lTJJ@xP0AxUSxgSN40_cGQz1=GH7LA&{C`fMw{;jIArHU-LEI'
    '(QW1Pprp~GzL2wK{X^ah`kIfKz^;)~eg3|=&+g>W;>#sF;!95*x6$#D`}O0rG8>-Uy)=Gbv29}w2|Q?m0!^&OAj2PSy@G2z!+#ew5A{?r<jzp2jQiuwY({42'
    'K3E$2`efg1KfsYdU?C^WSB<5z_&oYEd0e7N=dp{D_9w56HB7e|dHrZG+Ib3IVfB4lpF7x5J~TGFIHXf_bk~Z{97(pY)?B|m`-Vm=82ZcE(Cq<cf`oppitqH<'
    'QT4Xh8yAGK3KzEzY3eiCZEvZ?eJOt4;9V1^?B?}0d_7p<&4StIO`t3H*|5_q@mBd-5X<3<iZtkSc4LYxFfPsWPLTZpd;2x4<e_*t1Or>Tb_VZu9g<1(nVsYP'
    'mxbSz%YDRESN-!=V#Y;EKLuqx>0$lK;z1=Ud=BT&0;M&s;=0rWLVDWx0u2-M$%YeOi)xp7#UW7qEW-YunT_At?FE8yK2KO5Y%kFcI$W5J=?#F1`vOQLLG2cK'
    'J4pz8S*~_C-zU2rVo-*1;@pzg`iYPl<sP5VH(M0KbhS$l623oGtd@8g1Af(R;_PEIRfTe>XO?DPSg7{ia1SY9VA~CFvcjBcXG`l^E3jEi`4CHG)D7XN-twsv'
    'Ie-t3-u>HI9Vbmitn@6Tjt)^f+cn_PaP9xzGlKQjQKzTezaM-t+_>{qUBegqfO#5nQD+`tZ?~AvK+bQ%LR(+&ZcTW_t~S4AXFlFN`?c@T8><;PT)pgDW9$Nt'
    '6Ksv}T7&e9O?aOE4Z(`%$A~u7;mY|~ljU?TBjF@D9Ot3`W(Ji@PWQU7pLtN%B>^HkrJoHvsQ=vV?>3^|T)T&WHfjUGJ5RJ}KmED~wUGqK_8B%da}-g=j<c(+'
    'NXtEC`DS4xKmD*RY>$_5YgvN#QLR>cqwM$?_*DWScir2ec6yBc6<i%DHY`@b->cFGFedCzp;>}xhOM+1$$jx1AkBMy$11We=57@5*$UU%Qakp0*s;D@D)mzA'
    'V!e$3ug>9B3y0Na3xn<t^`nf#i=uvWkwfy?CTX3A#<0sb7dP^{(l6g6W;$2mwJrVAoV}elw1BkrtlZvBbhWL|E92?0v6(*X<Poo&mYGkGPKviBTy{UJ!~KF('
    'A`Tqi2xS<n*mrN9!dZ0~><;z!0RC+ci_R@Ke<#|v(eU~juBVIrPFXK=h#b3V+9QjS>4uGGhu@DYPB6n!TERcYcfS~2zub)3N7#9!H4J6gdoLPuws&RQ6F7G|'
    '`@aHty*Hu|yC2fYxo6}b{wa`VdS?gje787n&9L^Fwny`O?Zo>TnF;Vl;wN-|UHI<&0kmm{yfx~6dL_X~SlkZbt|I@aW09=9NDX5Iz>n?cr~SBgJL6O4HRsQm'
    '^~ksgkjW)Hb{&a@3tU85iaS@W$5Ic3Kk({U{iRLyyaHddwF@bob<oYVd{Io;95nVViAWD%VNBe)H^f)bpU~~5M>c3$pBL9KJ-T^Cw90do7=Mcbw6u~Sy-YjZ'
    '-N9h9zVGlI(XWx|cXy4AMWq>Bi?8Wjf_J8Rff2c7d8=<`($99b^Di~)kC<`rT~fKcrFWRw>s#=6Y7@)(4+OU&^E;w3IMu*bBU2&<YT4XtTu%pvLaYxn<38q0'
    'G@Y+b#VLia@<`mA&1d!Cy{-<kN*0SqjqhI`KOD}pHW#d*-Puu1-hFxXUnhC<|50?N&BsD<82&7#Wm={g6fvZvvLz`*FO)*I(xQd%*`NRO(z}-PyYK5_j<c=='
    'v~lKyGNdb2Eto_19o4G0^h;g6N9<^A-9|PkM(r-v$XkAE!5p@w(?d61yULD7gYElOYwV}zCuG~)dA;qAVez)4f68o>+KA*|Z7ts$<>ZhWK&_GtzOlt5b>d+3'
    'aVwCe_sk#cSr`l#p~YS*&Ny1OM%}u`u!eVd+9h6xLI<7s-NMI2uk#GOWrx|M(NF;WJUC5#!?KnHIBIvaisp++bQ!NVL>Kj&o8_hJ--s>m-c+|xs*}a&0J>p%'
    '<Yq~K2&`v_8@LPnbi<e30p5Tdlo=*yrb+X#|30oq-NycPbv%=agG%kAW996&nHEo&k%oVoG9mS&<;+HPmW)JcC#G1^1+O!nS`Iw=IGhX1emhEUavXs2?fu@c'
    '&)VzGItlUk;}tSB%KP|FdG2sout?dPLW`2GAaaQGOYU;t+vT`<I6lrSVBM#9GjsPRJrx6ad^N<9w$>z<?P7G*y&e@gYM6L>p-%8p;GPHh;68g0?NBpqmfTJT'
    'u>Ii5w|7ID`yQ!U7bN*flj~py8uRY}dO4#no|K2h8G?+r)6Xt+t4GamRSV3W;ci|{``OBH?$FLJ%QPh(@j5R~acDoHcZlSRcKgBo>ch*|&EM3=Z{Oann=yvZ'
    'tCe%V%?>BkEGohsoA^5yX7}Li_3&<wK9<)Vjz_te0*|xBZzW$d6`5_11EF?ZFO<WX+UT?KwS)gIJ8_dZl2^zoYt2{eqQ&RuU^X)Me=`;#q<FQ5@<F+NocEYF'
    '2Ky^~KAT0$UJ9n0XZ!Z-vZrdgcNeQv`*y!2UwpCFS@ZjjprGZ{WB)h~xW?7w>BgB%2r*!JCGwbK@I(#cPy3GaeoWS+f)VAC-WLM#m1-oKCtuc<3P8WM8k5I%'
    '{{r<bd8Zgry#9W_BF7*2>i^bC(kKTv?6|{7I$@?%fFE6)+ZqReevn5z23E#no9xkvfWYS4O)fWV=WC72Ls`*_#K7fYAF*bG2V#FW6Y+VSKQ7X%8b-&5m51xe'
    'w~InRqfQ!8yZJmr;5@IooibnL6yR4b9>l%~dXnHIcyuWiyKCSZGJFA*sfql0G>7_Z4xZ7qzu#}ZzdCzVegHkv=wR3y`%tYhI-9k7ZP@bu-Yem){Asmlo(@G@'
    '?R(u!q^P0(9L0ep5a0p<_*UNyPs(k{*OQDstg%gd=`XX=+h0CPus+tc-m9~G8o@(PlSaf>c<UPB-x?vRG6;Cv>-crqOW}0tyqw{o36(AwT-Zmq@|4OlB)kj|'
    'FhlQg?mbP)3^9IE7g|1rF%yGpu5Fk$-WD9<bNf!_WRvRJ9$Py(ZDz;rI)K(uGGf+anf_MZMp$E!)dBxGyF4rI9Q2VpiioT%=I8C0C#2Y`wOS1NR}Nf$jk<^I'
    'aF%IakhKl`O8xy<$CrI8m8)+~TA|0+DLRLi=0*$3?0d2hHwxg&HX>J>RDtwocxxXrq^Wi-G$p*n#``ntvyWTHR&HOUxYL!Xf)JQ#ccMAfH-hn5+a_bo-1i^l'
    'EORs3H#e7xcVRlCA>eQ`9~^I?4y2edwq^I<>H1Y?6i2)7lZLV-t7$8F50=$g#MS4^=%Q?oKL{LKo!0#@Amo0>;*ZZ(J+KazLIu?tqAs60qFwJ&eVkiMaC~b+'
    'Ic-IUPSl_;?v;CR+lK$1;AcW%!=zNy#W#4~R?{{*?vTu%uX!zlK<CuyKAJr?DX(>&?zJ3srYfjR%htMeo}(x3dX!g5bl99~V$>t?;n|HQLObkk%c6ll#}1dE'
    '%U#xR+s*D#Z6fpEr5p~I-H&sb3FhU++QFx;>h7-o0^frP=^TzDul6b4!(FbPeJoblWkl%LZBKX(*7$QLJr<nvE$Gwo4p+J_;|ln#Bi3I#oqqMGG>GX&LA%#h'
    'xX1`Te?K(j1rOFa=0C+}n!(*sO+ySEn~2xed?2Mi>M<l&-R{|{>Th*>I9mU|Q(f*Cliv{^8#~)O&d!rV1dEk^uy{wCTi0y>vH~QP_JsWX;pkw~nEffh9=#U}'
    'y)jV0=8(S=tI-C7@lRuo^fBUh>XKl^8yU~EJA40>tR<lhg;<*^JrQUaztPg+5};?*Z(qCFLL{2cNzZ%{3KYkcE-iKxO1UHl@L51HvL`&Vf-a@$S2}eO_OHVp'
    '34c|tppG@p_h7I$U2f{#v`B}RM}{(#a*`Zx88lgsLo@xF1#n;x^AqWBTWLmMHnOOcr5E^XGJg%)n!gwUJz05cc<MkpL++r`CS|I*XpQza+;!Lwy@#Pa<|SL?'
    'Fi1kL3w9bW+q0gC^3Wgq)%T4|erm_G?8<^0#K#43;d@xAnjJau9eRANRJ%a!p`bmwUAGBtWN-+7-c!BaPrX2v2=3RDz1=!GUyhg1HDYC#$a>G)Wp_RuP5|XD'
    'xGM@04*MidgdVJ}*S|&hHugeoyy5lrU&J&VD^><4N2xlC-~PEdoZ^v){kczNu#<MwWFX3!H4c9mMdH|uJ<bAokIj|zPt94y%E0|;L4L+zdhMfxcX_w^QL%Ny'
    '=uxo<{Zt;cXc|H!2{cbi;BU~dPJ8&w@<|h&3^&821+X$WPRt>FtGo5Pw{Ian$V(er3%e39R1m%XX44viGn)|2PLnRr+4D+g)+ZTPXc5K@9sECO!4$%GIV)ZY'
    'JLtdU`1btyH7wh`7+#*tV&<~#)iRTExj(0;2Jx>=6<l;KC}3W1Y%YJWw4nx6XLfiHc<O@^Z~3)*JKisXZ+}8u!p*5Il{CI@OK6u$otJIn_@;Wse)`0xXI1Dn'
    't~vWb^Ad6szO~p6sRMLjNVt_NeX;Rf_d+5Q$0OBy#J~Bc^E?{U0fd^Ozq~;j#ZfdOsrIUBbmnnoQ13h90a}>y+16U$CR}g7nNP>my3KxLjo)qNC}<30E?nC('
    '!f_uT8NI(LnnrlDEf|dzkP=A~j)ndfNO9Zmg>B+Q9!be4{Q0`zNBexDMDF7pRK*YQtM-#tCp(M@Ad@Xw9l7BC1}jrkyx#u=+-?e1S00W}_nOw2uD|9g$5U9$'
    'F#QSd`}lRV8br){+63p<Mn8agE1g^>8&f^E%<o5?9u31^5iB!gMz=1BPlnkZEd#y@q6uO|kkH>dQ+Bv6?x_c_MDykdqsy1^y2x>qZ|D6efAvY9A`kP9+`jFE'
    '1F%vm<itI1o24?qJ6wd~Av0zUNX)<T@1(WyA|hSIWmCP$`DS!4<{>v7t+U?8?Y=OLzrnA{G$57QyKtWZS1uaNoZHvfwl|OCPrU{2p&!64EkoKJkLl(j|Ap;U'
    'IgsRYvHngj_qYkP^^&vCKZ4NDn?ZVk+O?hSwnWG8wmEBPymP{hIsK~@`-&axZdq$*o&hhbdYv8-Xp}l--A!SNh@^{;Rm4@wob#E%X8X3@X76-3h3Zzml({Lo'
    'N&a+`C&p~Jyzn?8U!-W6vWASMy{tbs-e36GKINtv|G@m>#+!~up{e)fZec=Gm-?#dUCu|Nll{Fa40#PR5LlftC3!yM+&vq0`VJbW<DG=7M6OI$!z`CU@Vb<7'
    '0VNwiqr|p#=J%>ghBXi0TIe8`)%~#@=wG0GY>k!KjbgZcSqB+)qDK{#r?u@yAIjs#mMoS>h+TA?*=Ak+Oj;U&h~yzVjiwgoK5pp_An0g*&LLuT_;to`X&T+B'
    'VcnXLe(N3PkYcSwZeJ%ek$dX>2e1{I@r~(8Bstbern*~eRFVP>b^>Tfm0w}`eHkFF9z%a$Me5dDXLc63i?_Iu$Zg@b!h%Z<(d<ICQj_0S%=P^NW^;R8YggOP'
    ')~aq^+&U-NChDJF@ojteE7(*6KkQ)TL2kXOePS}cL*vMIZa@Pyb<UhT-WcoLulWjn&5&MH^KLQOUswfq`#^PtqK&6FL-op!Sr5U1(>#uRlZtYEOuu@tqybiI'
    '6?U5y{3DnxW7%3zqvI+T&yiebcdosK7h?9VJ>SlREXS4WIo>JnLF4LD733{?<ISYEP)6I$L@MFUC*qCXa^7{-d*W5BH?j=PF82soA-j9{=l5-8$Llb8TEkyZ'
    '`!s4xHS*l9)A}{od*kILjIq;c-g>0CRcou5n^h@pv`h)BVY~*w`8rrkR%@cdq)_LSEK6-*kAq9o19}kS1sw`uROC0|3VumvH|@_9<{Yz{y!7s3HR_BjpTAXz'
    'L3hrZ?ff=>z#ssm)apC6&T%I_fVED}G>X>I_K1*I()2Xg{M|4%Fp^-TSL~e4HDep9UO#JELlV43QkoqoWf68mqb8D`@SY1-enLD?zZgsJj?=9TKe=nb^Ja~L'
    'N3OfA2n}%f{{SbY@wgLa187c~qpL>J!z5`W&++4XPVuEqB`3AU;)7zfZX~-6DF@S9Ik;Y{wZI=6Nyi*_-!O<b8ptltt9b8FIp3TDP`?AG(b<2u!n5c+<APX6'
    'bFB;A>EXOq+^KJ=2F*e;0QSCk9M^}2Ce(ZKaK)N3zS_dKfZ~2>BC>|*UbgZY3duvg6-}n)wy}R6+c2gOvtTv1=VIP|xCe7tj>R%uo`*ebAe3*Cn^b5M?}qrc'
    'wQP(ovi^gcQ+csmCg+*X4{?kD3aehZw;{e=^lOSiHJZO1LdDFUH0RxQyV&IE>kkG`Kig=!{d{{5^1#H!hpuqFV;Rf+*Qqv@215r6-%4P~x!&$KG5&_Pw1)BA'
    'PfBav=Y%_MOy)dZd3C#<K~1R;xy>|hO2ggc1S}+<DkM9t{INfhmFp|BOQ891zA={K<K%+Lw63n(??y_NrvlS@@27BBj%LHFd>0p>$f}{WNuvQ<O!sinA6@{n'
    '>Vi7{V6V%Wnx*j2nN-L4@`_v{5FJ&Yc{p$t6xAP3ev}GI+F~oytbgQSy4wW$#nPe%&V#7|Z~x^AQj-XZ$5DrKZ224V@7)ESyqu|EQtQE4`%GoOu9;@`_mplu'
    '^LDqW1AhF?x#Q{>-`juVv60{bs0!0^IO_4`Q(Xi7mxM3Tm!52*Fl3*`bNClf4Ggu}<qA6K&sx^~vtgcDlzQja?bPW_rPD)d2jwk^l}4TW&ZqZJp>8xg7KW4C'
    ';d(#x)Wu$g<fW3;qv&H%-=0FxMlY$8c4&IO8-O8x4`M;uvW!j5t>*yZjQYjrt4F6kL<L@Mr8{Iz3wcEJuyKn<w&Y;C+Gsw&Mwm-+ibg~8`Fc_9N=TKscgy{C'
    'HOZCjYiqLgLtNRDaphHY99HpjA|Dg;Xf(F-qWy!d{KSP_{C0D0<UVSq+k+2JrysCExOOX~?z`L9B463g(xQn)t5)lj|6YG9^}4fOb}`t440qy`CW~pAHyefM'
    '^Ta=|r9EMvWhmZhtLS#gzd_u*)Cud*qn0>&<GX$+F-x5529@Prksj-OUo(|q74JtS{vO!)S8(9lYbypKiBfRChruVLUZm1VVQWkNbNZWgE-v`jfSo}C#l27G'
    'VRVm8BsP#@kI7|y9j7`I9J0&KBs9)vLqRh(tuwP=YyHtuIq~bC{^2404_3p`GdVvKCwlk0CX~-wjflyh0F*{Eqd(K8xMl7~@__xTPQQB49jwh1*CIMb50JR&'
    'L@72b)lMFB90ss}2xlvxQXQquI0xD*2dw~?m)0cNc_cYS^89FE{#SOk;?tK=ImRj7w*XBek1J7+ZQqNt1H{i;#{mCO2q`Wf+H=NbPUR(K(~}-6Y3H;C3$p3|'
    'HW3m_se^8jR5likKj~`HkLKpGc=+7~kEddPsd3}A+l$&Jv3&lfxyQ=bl~RD!Dy)&q9Mz;+u?FGI@92~DK@QB`$mpZ@<<c6yT%I2Mp~>JS<vUdmhU<YW)yR#T'
    'L^5suVctx(yza94O`~~OsW~vxysc>K(ms6~yS=zRmWX@bI>3}F7Gf6}&ZiEW9TsXN%I7UdCdEJmM$?RcY+LuFt{4KaZwKbe`QY)Q8kx`O1rq>z1pN`g<3$1`'
    'FJ`GZLSl|Du=5_);gL9W^={+><w|{p^?{ZE<D_~W;SDRAGlTqW!_Tc)EIJ35w}m>@zq^NSA01ZvU$9$&nW1;MTmv9v@5(CC$u|(~2G({5k#Fp78aBxzZ_BU#'
    '=xDt8L;OS5QShGzeI~uYL|KQTs9-Fz18ura<A%3l2T4VAu;G}&i&n(;f2+-La(bmo3`%%S1*+$YS?%^MiAFa2k-5Z_8pXe{>e_qgy-Ij<Yu9vRHZddPGA#zN'
    'i;9a%N&o-pI1wk=*~I3}HiP&&o8K-9e;5wwr4(q{@4kV^*;@eyd26<Ldq!m%^OMV5@FD8Zi&k`wgl(hN%PIX)fz+vsuJRiD{B73zoGCPM!Q7!$TZdHRip%9}'
    '47$PfHHCuN;oWOVrCW0^`vJVIPLtQ)&_*ZME2p+l6D~&9ohC%*g-))A`>YyW9{dn$*%{6FB*3nk%Nu%|sD*#z#nIg{?hUXB;Sdcyky^i8KIXbj+p5U(Ke5ie'
    'yHJLYK+1(qCI$oNL$)7BDS)1W7$Zuyvu@UQMHZt`X5PQsL<Oi8wAF?RfsY3LVX{UgB-zt(u{e_Im)G4n2;lGi_O%E}Y`EG}?_4hP!x=n%rUhNwd%zuswf`F}'
    'y(TL2w6wZ};Sj9!_5-N1@qpc+T7PHzX!L*gTi4w*sQ&gOhXuxnY>ouV(O{%S2rbsP&**xx1T4hE(e^D@f&KhmhbQeuJ+<);&FJhAY;M&7+NN$Lh$@)%SJL*D'
    '5<bi6kjdFDE3T7n)e>WL{3g5A#p2@NDpA97bvD}!hF#;1q_@OYo@2g~(XTNau`*43n7(wnhZC8z4`Vhs|5emBE75E;t=(pa3{Y?dZIm^BEpL5Kg&wwlqbkyc'
    '+)L?!1f%)vW9UlA23*}7g{S<Evzl1ZDICtT@w;7Q(YaUf2uk+P%7wc;DwWy;O_qfe-4*ES$_5xP3h%xSY8AMCzHeo8P3b)Y(qr_wbx%*VQ^!PV`?iS)Pm_aH'
    '-A^C2Pg}ZFhXaC3>%(e`1*@e$l{JT8-PB88k0}03NoV2YKYt&M+wA!v7GB$0A0ex54J*!YVVf6cwlyWv*iOZo@-?f+bN_Hv77O<P2@`b0C-csG-Fm3>y=x!='
    '2EW?M>d(0ff~5on-u0sW$R5)NFFIlL9+>5%@f_Uc>0Lq(QES+IxO=(sc=Wp$>bZPh;fq3VWh$PoCeZrBcCze3-*WwiT%NN6D41X|oz;Y_K0@jrb45t)tjqS)'
    '56b=}^1Z2w;)DG|zG2fafKd&@{u~I{vF>f;8}CODp<EkL>fc)XZ1}Z9uvRf-dJ5Mi*nZ|joQ<Mjc|&yT&ZH&o)DN|_3%OhLdsCE4E7gLwz#d)z7m%vIJuKlo'
    'cFrvw=KBHzKDt3BZTG@;I_Dc#xNZFUv(|ZHLg`|<SzZ?%qIXw{!nq!^^+I0v(3ozbzWEHNr%t881B@toWpDMIiU(})usbzpU=E+)$^a+N`N&{s(Hs<_+?&C('
    '2w!_7KCNs9)g4Tv)1aH^cX9N1-SJ`KDXuYj%M2s((-i4iry;+;6JUdfOnvA|3nnN0{)!|K_kju@HvE9+#c8_iS_BenlaYMr!|0>sMzxmRbV%^mB(au#;xD`T'
    'x)IkNzZbdiIMb?l(y)omjso1R_t>eTFR1QY+iF$lm{^<YtK;u=6zC=NU{4~Cepn8+AA~4Xs5T&U-yg%u1}GF#WH+We={EBC8hsf493a8!sVut9j-;~ys7x@-'
    '-5$>-g_@6QeaG43XzlrkB+Rwnbv`GER8*-)l|S{T%e%o=0%khyXIKLrQTc}6RyrUyJiCv(DL+VysvhmXE*9s=;63F-(4I==XDt74sMA;*${nbmKHs4;-BP_i'
    'u6S^*_DRzB3dt*z_@X!Fd@h^Iw|(jU+L!m4)hb-E+15thbcVv$=k1D(Vxd07zM#|+D_l@&RHkz7SG>LtoKQ&9ZQP!0Cp7E_wIou!$0-w50JUq>=1t-nwwC*c'
    '*m2dEfyCwqZ6({VNxk;Zb#YA4VpP2%ZFAl6a7lk~5zG9vEA-f7_yBq}>Vw&|vyJuh@x+`l&d^_jY_92_L0D&qiLM&J@DEt)@0Otd##Ia5=@KSph3}U*DI<VC'
    '2MM%3&OO1k9i8JFtM|e}Rs;V%z!sjeH06fU122aO>h;fYYr6JApk)q}^1=>Pm5TK{R==AY4Kzrs3N6r6QOUGNr`boOu5Y{7$8sK!pDj9MzYD8<)NBK5=?Cy!'
    '6CJ6(x!|wk4RJUOY5ugV?DQ@-HpM)3Se-Fg@np$SOHr!mGPpzq6Ed2)1%}?T*OAVQ=Ox?&8a-##x43=7Z=oY337%Q7aYt3XRa@WE{N>HuV*WI>sBzz^{_KLJ'
    'Lg_yKfLku_`)0d``AuqY70_Fxeuc)_t?0_v0zXD%kWv%acq0c|koA0is@!JpwR)hb{!O2QtoK6y5M;WkG_)1&tvf&^S>(+h692FtdVo>AA7n+~wg<nR>FtV9'
    'Ys&oGvC2+HzoZxJU$Vkoh5pyQ?hi3t@@UweH75t&Z!6(+U5(HEaz$h7AHl*}{kIa!bTr>357_Je|J%Q->I}w2x9M=Rfse_*sQr*XYSrdGY6X^Od+pq1jbB3l'
    'UG|7uu8s`mp2hXK>j0})SKk|Q{8-Jcbgt``NzLL{Ueq+oxLr15ZNK}>YW+vEjar~xkX35aGdj|T0~$hG@HU^<ddB2Iavd`q+~xS1GkG6-8)}^rGke61@BwNK'
    'n)KJW^|n%`GPuZU>k6wXx1bXWn|>YOwPgj-->oU=S1X7nSlus~>_M>+YMtz4-OxLHoY_*%U$rkknMK8Ryb*Muez}X-R$ejNcWKV|R-$~r7LEJ)LRCqbW?t7G'
    '6qME~9oOBrM5)WFGn+i*&b|GO2T*V*dzQ3pR|v7s#!bB0{;e^xZa#M1+E#gT(nn%ij%W8I-``Irr#825S4@@4?u`CTC8>jU|8Dc8Ml_)`5kh(nRyW$077e>I'
    'X<kJR*XQR8P3!T!&*>@D+?qZu2kT6+(5x5PudMjk0_j=3?(gnhSm^XCZR0VV2jlhp;QSV`xW$I18zl3}YP$rs!Y7Xu1l<y8Q7n4?eIQrYiPV{|y}Z-488=!~'
    'T&!LDjF0VIP=BlQauWEExXP=QE>WpOtqYW4+CHT=w3R+>`1ZS37s^PPC&B7{95nCTlzgQg?A}Ze`oy~)ZLa%GW7%Vjx_aA8Em_#KI%}n4%ZEa`ByZoY<fB#P'
    '&c}dpdZy(M@71e`z+R4xDHB&G^0<B4efv=yoDaN7H)k4VCDdW_#Gb*gPTha`;CEaJv;FRm{e|VJwtUA{IVrOJ6U;f9SYH!-mUl?Jq!c;Wl9{WgKXDF$%AYVP'
    'm2uY2U}OhbRMYFEEn3-C)0sa&X6%-HH~#Et-FXkwD}umpW|nOSW7WP~hWX;XQ!`byF$uGd)@OR#ls!H<uLY*369V{j#(D>WJP}-t5H6L+FGei~q(hEh3hvia'
    'QlP#5wrqtSVdf_S^Uib32De2xuJ>kCk8cOnMl;*4&}H=olodB6+>=j>CxlEvqAGx-k8`whWVb>)ea$g*mh_yiebd%I8=6<QvXJMH(GHo36T<g=uP{j(;Np98'
    '8*!m`#I(5u*6f4c8mCQs%rpsavRMV!@2ep=^U*<^yxcSu{sOA``5MNF5~mq`i>L3k<#KVf<$F!ZX3675^zzulz_h8eYK`;6-4{+;bEh(@y(^Yp_t{~W#Tu$v'
    '{+7?$V1~K+$V6_GK8FU)0leJHiydOQfd@IhHyrZ=ubBzW=dfSjyodQVsjCP{0P3cY!gl&Qfa(RIcfPqkDJyGvy`*4^snv7<O^Bxi2<W%>EIjn%!nQzFXsafP'
    'h3qDI^FVLBSrP7-ou!^7Dbl-Ya)ybKHcSPmzWFd=gJ0h_r&kO*x6P@)xIT(OorE`?f!I=w_i%uKwPSmma0h(yEh~d3HLxi50!+_B)&Gp|8n@K0LEbN%%YHRk'
    'pQ_JxGmEO05UVb?8r)y6@qN^2H*o`Eo59-OYxH;;bK@~4A0qYBYfD_DS7>%U-pdD{p0euBWM=S1ZG4gZl{w4id~i?h&~9)ujsPm0U%;{5ZF)e~YCQmav78@4'
    'XB3*O`ncdviRp~QbZbmT&{OG_XR0WL(+KP>k$AjO#@s@+*)i}q1irpp5%L1S&S>5UA5(0}g;#u@_Eyt{UmN$q^CR3etW`a5DR(fLBNw}AaPLAzCl~#3vrh4m'
    'EPuC=`ugUzrp8GEh&q?`%D-fR5RT7cIxj8mGat>8!qtYgs5?}?twLcQ>mWj!Rrh#a$~R}{0|=NL%*LgyaI7$WEJiboo&aqJ>j5X<&#v3}`UIRS#BNXfeh0pV'
    '@n-e72txJ3e^0yXtb>Y0+_6&P=5HvG;?xy!RQ&3y{F}}5>TTg!8<|8c@u~*VY6%!j-<bwMZkS;9aMLq<wo?A$?Y`j~+<UEgn1jM|zMYA9?flFEZ{>HGjw|u|'
    'U?{_(d%C^z)mHwCeLHELJCzRJZ&~+Iu?z1j6!`SF+j6TSd$j<aHDU_ri=7?rr~aw8&K8z?MJOdSc_O_Fh{@J#XSiC;#Lt@Feer@XTC-6Rrw8};F3BbXYuIh}'
    '(8_Zy1oYH-zxu;LG!V+#%UBgOJT&&td^FIKo7A3U3`C{YXd)1I5qD#^fpporo$S}^cVqE@2P{B5#EsO~N?Rk+vhp-rFJQ2Du{^E68_Eo(roKugC;q{U<*pKM'
    'jv90>_pSBiFdcbM?IZtOZwT$cdV?NyvW<Di!{XB+D=v{nQ8skJVZL#>%P`HBt2a_z?GZJd_x}8AV_4z+v*bkJpe5D?DGj#};l<QRO@wydElH*vw2K$2^~^54'
    'hxpVJ@Otj>Z12>aTc<z$h3ebAjfsFTT$F3KoA+X|8*wAXX3Wny@Ab;Z{kgnC_dJH-e)W&kxy#505BUAq5_X6Cd3EjL7{7V%-gni`Qgj?2cosp5chkx0Tnn;|'
    '%>D&@KEAJK`BG$82|Q}Op7pUg*4G5hauYFW)@-(QK1465R^Og!Xu7G1-Rk5y5+*J3c3$^>3<=1yY1z3A<NDy29q(krn_)qf_|VnO9B%Z>i6x$Q_)^!0NJSpV'
    '0XBCIM=7Wt83+jOTiMZm+{n`c&nCL3_j*qm<}0}qXxhUYO$H2Ej5ybKU$(c4$KB<niq)*0`I%f*W1M_@%iHF^cqdshhW~<H8+9)~Y1^Ba_k+-F-0JQ9kAj!M'
    'iSAly88w!NpgK0`bzI*9iamV7bd|a^uVmeO$9-dqgVb(J_s8g|UCZTZidOo?6-L4aK5NdC3}&y+i<0F-rT3yX%A3a)kGi(>KXv3R^nvR`s2-F>bII?!9r+`j'
    '0MB?lU)q>7!7A4Mc#>UJ&GAd$jnIJ~AqduOY`qrY(YFGvJJ@1yMik4!9B=IV-l<iz&E2-W#YGH-pKo@b)Q*SmVKES=L9OJ=ZQyCtLuoO#)m=BBQC7ST)Y=6~'
    'pmA*g_S&j%mMSbSvTS&NzVA?4g~?<Yp!DNUxaO1e#V-JH<qd&v8?Dj}Zc0pHyrI~w?lu>iSE{T?ibeV$-=OJYKKGr&2qx>-ujoIThX=Y~yVKpCJjpGaWNt52'
    ';8L*B?(oU%rh&)7h(6=A)w7f@GTS%7KR?Q)5}BIq4_rxy*T=Z_N*v?*s@AX<YmEHz*_hj%%CrGPc>t?mzHUmRMz?y@V4!Wko8#Z!gQL%ho?2p<wUT!*VWe5&'
    '{+MXd%d3$$Tu+vd9hOeelxL-S(nMYxje%s1On_EI+%B(eeZN1Pc)9GL=9}<Qs`ypffY&=d+x@6<dOl#`Yh7#h`g!fXj!Ce*);fQLFj3#Nk0g8`=DUK<_2>cz'
    '(v>1i<I}Ml_Udt`rWQCdE0q<9j>P0sBbTRqvsvBYUA{=H{X4xmz_Sop$6ck#R_f0V)O;@Eq{`c;SOg{_EKdOlR*sW<y9N>bx<!-8H?!l%{6LG2yk#e`J@b=|'
    '{O3nFtANsVc+lYZcz+$avptJcX5p-i2!@20={EX=b!(2V|0fZ-DVfw^Utg&e$I9L;=?6N~uj=LpCM;dt-NxaxmBtMt*LxmGXVayRa9c!*2J^{#doId-dDk%}'
    'DgMOE2X}dPLW{Zgsr<n$*CJDi<nX^>XN59C8k6|IEI-6#vdari`!t7>wZ_i+ES_F9h(|l!q_S{?*5;?MH$pzkfclzKtvPerO-66x;5O{_B|yHloA6p4m6O!L'
    'DNf2Nd3+l^PO~Mysy1rQyLvqMg?XyJHbBX4^={Ct8qB(}oe=4;Dyvh@jQ)b`Fd;<T$QVN`Z9M?T(2^~Re&c+u);>7?MIze0@y*$5>J;~9pJ<Tw>o$tc>EFjq'
    'N^HjsWkbcgwM@W$F?^nPg1Xvv7L9yFxFlG#wA#bP<i)Wu+j*L8dTo-t;-hHSt7%QR!!J?c#VYz|?N!gF7t(x&{U$73BbJ}E9O312i)Cne;Z|j`sGiB7)`w^H'
    'M!U!L?)hi3)7QBI3Ipc%5o82i4>pzEzFRrW2f*PmZFiZA`4k$0jV<;pC%o*gJ6o(~W)Zfe?YhsJ>-zG0M6&6a?Gmq+>HGcV=rf_NI@W4Up9NjllW*>u4LsW4'
    '_J3fsI1opmx;Sv2b%Up*yLl=i-e1l-_(eL^-;+a(h}vGaCr0bHQY+c|Q)&FMhY_RL>>wn6Q;&dR-HF<>DSo7|Czb($<Veg>D-<<Ia-Lbm(k*R9QsX{(uZuY<'
    '@$M;*P{*UO;xE<cS=dZbZC2~%+{EI8iTkqx$}o!aC0rMO-7y6hx7%m`LTveZmo*F@h9T1HP>+v@K)O?#hSl$5KLvxs>fD}#cr$r)n?0xLe$y2M7zjSl9gRcp'
    'KSaHA``Dp6r~2dCon{6;cQ1?XA>U2W%Hyonzk9kmWYgMmOswJ;&bfs}kM+hFNc-qXSk290e-FFY7b$g#!>gWh&ZTgkmB(V7w2S%x?$^fJ;1D&XFtL=SS}FT4'
    '>`SUs&1%rVh{`Yn8Lsw!3mEPM1z*KxmXGYddv#M9&DSS`_0#c~gRRkH-14HFzsw*dNL19o=uf?9KG#LJxHig?516W9Eq>zak=g2}L#v(9ulhO<cG4hgZ$nrb'
    'A7P=aW})cx``wm*b`)#8{AydpF<1VXe`5OlPI)z|kwp68y17)q=kATau7)>REMtkOHQV#JS%?1Qm5&GKN|%FF?u#5dTQGCY;nX8vmvh;<(`c{JS#fyfG;j~c'
    '#}JYLS|#@T!RgbvbHeaZe8b)Mesa?zGq#F2X7frECUJ+kblM#PtQ=SUeyt3C>ZRU3Q_knTGeRiW=4czrm*B;dsGD8ps_>a{lQQVy>rdVd(w}=428(C!d0c}l'
    '$(i+PV}kJ~CwlN<tF-V$t4Qzh3z=K&DSOmh|6PW>QCJh%eD)u9IYapmdSK8=3$E1cv4&jWLO_>w(3^Y<X|X$tH2NnR2A**^zizkE{Vkq%n{;a-du=B;{7EPL'
    'gVs{uan8&m4x^yAlThnQ0(1N+$8zPx@Iu<;SOU+c1h=cshWtlN^m!KQ><I^ziiDg>rczrN!3lB%TXipcwmsJ!p4yJe_j&R?VZ#kP;${h&nw_WKx6tM04z{C*'
    '(>YCR{gzto0$W1An*^TJYwyYBIqDAEz3_?p58DKN$w`_*by)O+rQmI6n#OF{g)+6byJbE&&j(lQ-GjxrHH!ineRMT*_e6mu(t{6h+P!4Bw7KIeJfeaMzub<W'
    'Gp9(FJE~iTr#3RT_U!YCT08pPX>51>?;#YEzkbNn<Fft9xW@>J@z%Vz^T)^6F+NZN95jqoK+e)f`D*y|DoiJF#)l|fd$!`1pQZB09uc+L@3&YcY;uf(zw&GJ'
    'ejAd>2H)WL+R9JZ@tbh#Xg4cg^firl{^255a+4b`4X;Dn&V}dSJAP3YkF`N3>Q3j%$8678?aS?8ujlZEXJUi8rVa(XSc{i@l3qcuw>iV81=1=vRYI|o+(&s;'
    'zW^Y>am;aRq{m^RrU2W^=CG}f;nd!hlLI_Dns1S!@jc28JBM#<QP%u@{nHEV&&d#<+CT!`r|gh{+RL8SoRs^q;OpP$Tx3*Oy`YJM+0;rwKJrqh{~!4P-44UQ'
    'K~jL;J2Ux;RVWsUV{Epk<jI!ckJ<ckJHY2>^ENvp$chzI`r$Q+IGr;S0}%aJ^R%AY83@jzLml$1dlIFpnp60tm<fa=LlTdKI}z8|UKM)kTjIuZCzsTu%1UoB'
    ';O6c@`}_P=dCW!U0QI4B!Re#(V)c8b^7$Gxm9INAZ(N{G2en2mU09yJWsAQ^_Fq%opN1PZpegx&<bVARbQ9qcTR|SxBLQ;S2%8Oar}yKTIv>JEc~9)|Jy(^K'
    'jH7zy6HjmL#%~-<^^C0quor{ZT}b!Ck#pwN-af4?F<zXlpWpT)nafl1mAloDISi-V`nDxddy-?L0l8n-s<WN+%~yvdRe1E;!<=37!N#X0w0=gF+6ue3uopTb'
    'ySlQGJJFt-7MC=%g4aIVhf8}oZ7k25WdgOj{m&g>YV#e?x|1s+TWI<uH|ctU_$N7QJ7U!`=;3cST~tVhY6RKz*36ua&>Tn0KtAq0j<?^3mxN9R`@>(Wzi-q^'
    'Kz<qCb4A?Q^hfR~6K$h1vApVcGHZ`_uSAA7S2ty$=O8>vmx8(dhQr|az_&KPkiq^}rpNOd+J%+pdUak-JN-)K6(^S`S!PS9wcj0UWHvbG;)-6^>5`RMY<wQ='
    '$**!X+AZe*SD%|a-`I!sHY3Cl;Z1QRu1+krewsad;s%@G(yqftNN=K{+K=J&=UmRilQU<aXlZAwVAmV$H`=B99h5T`6^c28biC$cSL!uFvOm&cLbJKQC!07r'
    'NY5+%-YD`XCc9E_>f!5)Duc&sX4am)cVk6#q|QY1KpzVh({_FekdO5}&Iar+(r1{7>>_ce7!r0*tKOzNezYymA|EBAR))TvicO-q#kZ4H4%5(2RjX%o*0-s('
    ';XK`DWQSRzih_>BMs4u`CGk|Z{M}NY{BWc)mJ9iGYK&E+XzWL#ecA8FhndDu!Du&sV>hM}C6<tNVvz0e3kO(gAP>SdHdNjcG9fIzp?u{k*izJzNl)OzXeXC?'
    'G)Kc~sJ+j(TIKu#fIWG*+SUzh*0+r(%m+Ekl)S_}Ao8;KjMv!@IRn!Y-vQdq-lw$|n$&x11Pedk?(zuBL$ZG9OZW(YlL`cRulFxy?@;^pH%+fq(O5wct@pPX'
    'rXEa8VuyUg#wX#SxIO(UO17;cL`R);GN{*O&bP5@a98*huz+iLy}UJsQoZ>aBxKmQ6C>NA-|44G?-<&)w#p;&oFR`Yv)C1u(HyzODS?99;kX`*@!jz*V$S_|'
    '`^h>us!0}8R=>f*ew)&5(v9Ws%8uQ*61d%JPcrwg?*c7vTM@tx`<7xZ<eN7-YB_Z=;u_I{=|X_BYf*$`>6O3Y4s4!p&ptQ8VPXtb7b@4?HTcmiZ*&GkpXtDH'
    'EkBiE&~a}Kl|J>m2?7W^bq94*z_cqVGdVIwh_#KY7gc8HTcLQAnNIt)3d#|K-D7yYLoQ(1%Thc1Zo5N$R9gHZtNGZ%9M&g98(YQ27p=Cp2nAjj;(e!Z*5eBG'
    'r@{lCNX<>>S}ueezQ`_5S)K2RcE?sAvlW5fW-wjo*!{M>!Z-vu-3@j$wn<qVp)B`MZ8FF=vyN^p@!Q7}2C+qcZBsP(v$xsFy{~cJOrX}OqFr{U`KG!e7dui}'
    'h&^0uxR1v&JQfnqkZ*o<l$AxF90Gn%Tfzq5e=CZ=eQn;OSZjQWAb8j9p#PNcO*U`ggRmHsSikHIe<<_UEIX{y38>qrLN8jQQ6fRz%L-%K<#I00U)>!*eCPOw'
    'Y@27R!spa-)jV&j2lPtgT6W>7u)g_or{~JIgLJmC=e?9V>y7x`dyRLU)drZNuv66+P6^yUJ+gEDLDlcNvg@tt4Oy@{wMz}g^j&v53);O@5NnI(ymqS$4<vT='
    'nw^E(__*O!<}bTNg&B9Yp4l?2HPDqC2`6{Hu`@bWm5^<Qwc_*{YR+Q(FxQ@O_M{Lg$eV~QDZS_V<oivW-i--0RuAnn^zM(Pb$-h7X?(-wAC!S`KEh0JK6|?J'
    'Rc7Poxx#GURWyCJea(9fYjsGWC0$S{S)TOsRj;2{<(?o6Rq6|tl~?sZBOJ@Eu!-62uybzr(xJ^2tcvRs-oM!gOE`SH0)9Ap$cDV=r60fabzNxjlf56VXMuNu'
    '>N$FX-m6a*VB0f1ENj0aZ8yhX`I5@Q!`~0DWG}|T+w}JMQ_ZbAdlt(PzlSbRbO{3UET36w!0fM@@~3X6;VGnBPdMvy7`^y4xba$)rUX<t(IONAINeg3y9kP3'
    'XGKI#PiZmlaWW25Nv&qw?em8QotPK{JihM&qd@;{8iZ#(HX8NuN98_k-bk<~>XmoPJr;w;{eDB&WZ=MkbH34=*p{0b#V?KTkDL2GVW&ifz9BeTx7s_d72S=t'
    '6^`|`2G2%A;<0&@b7+%#S=c+Zk8El9>iLy#)zNPG{)9u?$eLW+sLg*i?x#!5f81N{f@nRt>0@fl5utOKP)@(Oh+koNEk?3+U5>@qEo%eo)3Z&|Xs3#eAn8Q0'
    '79ot1m-l+cYBmp!o;h!)m1uK(!}r=%c2xS%zfM2fm7FQ}X7Icpd(NQcUz%@!0~9SlzwpxMpioM&wB*XPw&8QFY1!4+u(wmDm&M~5DP1rxX?hz{DxY?pGdadu'
    'zy9yCukDKN)o&)uf+(iZM<ZcZ$W>Ze!MoChvL+yZ@p$?;L-g;;)Y42q25ZCGV$3?ykopZ4-oF?+RQ*_cnQe>QI<JukMpp5Zi1OG90`yG0FUUwT1OsY;)V6N4'
    '%RD*Ud*-E)PCi0!*_a^98AdGWMpxuLq|3Pb(rcqFQD=eW&8PdX`p2TveA(aaieTX|=9|BYXrbKq%(Ch%H?oSO+6h<W#{nAbYOf|1-v&THCEU6pJ$@P=QZIWX'
    '5iBs+UN5^x^`bG|9V4nGK<5Z=7|$;w9S(dv{bIx0<D|`x!RmRvCWnlh3?_ezehWD)G3~-TD1}0o61n1!Gv}Q<NMAfu)Q5|!xcV&KgkO2k^FR4+emcKKdy5O('
    'E*%%hMcMScY|*U^B6hRNzF&L!5PQ`tTEABhVny79lg46IpmKMLE`*&VVUZLyv3q!IVzozie9<^^B%E(fr{C<v@_S%=3YD(pzby8HuUa`pV}lIG(EWZ76ZpNy'
    'bLTrTnMkQE`e&lgp>sbJtBdiJ{+wF{I>5f=;l<b2idz$@n-+9SVYcR@{xBPI%4;`z8NYW8uokU%Wq5v#?xixj_dm+0v+IxK7Ri3_9liJn^a`2KuMP4Mw0Jjp'
    'PtbTbJ0dZ7=Ya8rSb*@Xb%KXnGFIo!$}$^Z$*FqL{XZ9&_cwydpB{1Ngzy+#VO1f}4P@NywGR6QvjU~*SY^A|x?eP?WBpxjex2F0Z9dPRmQQ~dq0(}}=Lrhu'
    't*B#`X!W{_2wR)7gIB8a`;Al+&F+a&Rr)iuk5nDgfySnHjniwR9-}8sXU<c*96s7v6r|zm@!&M~VbdR|ageAzvLTj}SQS{fQ9(C95ZVmvO4dwlC#1CVab7yJ'
    '+xCF=v<)296laq&|M<GHWd)UF`z-`QpoS5EA`l>hs3?;-qC7auEQmOQ`t8@#xBK?#(|!AG7qybis>;e->tV|UBJ@Mq!%fnfA>w8OmF(J&Q{0VghD^yfyd)a%'
    'Z#cc(wh2(LSh4&i@v1IJ-E}bRkLw8ILt%Z>Tu{q!w^Gnfp0PPDKgrp!Xxiieu`^{S1U+XtIuPT@8Xj|!FSV#!ztubQ(mdNeXLpfP67hR$9$$4q=4514y+6T*'
    '$iP*;%wF63>d&J8T*u4xOL`RVqkC47>JfY#$n7e6&DU^>#>jLA5e#U*_S1EXP8MHfHsWe~F8vX_&V0|<<zme<$crPek<AEA<oznBlIsoKY;v}Bg*leX%=HLc'
    'pKyayr?2{G(TDy{4uTi33kz-H1H~g&yjB}o)BY&8%CmV|eQ<h;678GNm)rN@q~6zXy*WQb*rrrDbWuw5F2O^&mP%J)^(@`zSL-o%=QRynQ)|S%6~!E<09CsE'
    '#I1G<;!@oYE?q+pZs(Tz58HAe42kgiSKBwbmVe#||8~#8{Nb`q+(#eowy_zu-qlc$Fwlf1Ili4+!vmMUSAPl!CY;t1AkhY4`_<ACQLigriz4(t`A`dE0M6hG'
    '3;bsv6-J_3^n3Q#MgN}<1Q!?QD?6GY{7h;t<D(=ofBYcdwE`bvH*77-Ha{bpJ#6VJ%aT1?zt*E#vk$cv;wl^*CzB-ySGCem>+qHF@wlpPul0&NoirZGtp%At'
    '@qE4kRC=_T^J=?iq=`&3QaI^U4${&2`|BH5P=cVW^Y`I@2;;Gm>$zGxFaI3Xzu=_vP9uW#<&*zg^#6-%d;4o;EB&`s4%X(T_R0SLFkZiIG@$P^wB$-%z4zXh'
    'cMovZ&&bb<8&thrHm-k{9|s`SHum2j-;_}*nBz7tF;qE_9dEv7Gw#n86SvA-rs1;GZ!F+{Lhx84Yj|vawrki3?iy3zOW>Om_FsMQQRVtaT4ewE^?!g%K!*JG'
    'G%;>jHbDR4=x<;dT?n;5vNN2c;OHBQhsWu!;MIGyT*K2A31H6ULua3E`>)`h1|eeQ6_n=hQa1>tZl!b|nh&_t=ZjVawio<-Gu-Uz-F4yqcZlnDX!=%sV(2du'
    'zi@$l@14E#ptB%}{|-T228jN}(S5hj-|OLm9`VD)Za`|ZBefTDF`~(Tu`LD<(3}M)uc8_MZ;(q4jA=w_f=BwX*m{=PG{S!ayE4tA-=TMS^^r!%hkRFge0jW-'
    ')E)94W;%?xg0N2%w{?_u=|^2_B`0oLM_fEyEZy`czY?KT20ZMJ9b_<!eo4wJtycHnzzflIvof#z7s&J{r#_9Q8;ikS_~p=R`fuQSb2mVM4>8{~k=t)e_OsqQ'
    'XjOmNG=2Qt%<hz$fHcm-_E@{!iuZm!teNHEU<L*Q{?@$mcO9J-o5s$n{n_lF-Z=JhubmR6)IUBazYNQt|K@E9enhSRoYJ?4Ii6pa2=ss67JoPE`Y4DNVtlF8'
    'CxiG%frbLuoh8(o?=t#DMNexDl*S?cTo9}lO(*j0Zifd1Z%p6BiwK$orjl3uP}z=H+>eVv=Xovft*W}m=qH+o_D@G8^3L7#_D^?Vd$wO*q-n47ll5i2+r`A>'
    '*hJF2lMQ0v@;up@2ga?6mr_k-umy+k&J7FL?;Z8q06U@iNtgs{Bvf9v;&h~$h1Te;CMB7;t=XSWgzImi{QhjgUyvWbov~WcJ|wUv0Iy2lUR#6Og1Vz@akKIl'
    'D17t>JRJ>RF4dNangf~i-Zt;qeBR+0Pg8~T^d`z!WvcQaxA?lzy@Ykc^>}n=tC--EM{ISzbfx0s+w@N@Ehh8p?p`C-^Z7WBkMdSV&X8MsP8*M7+Mz>e4L(x+'
    '`K*`M?MZdVFJ~?%p1XXXR(p|Tf9iu4j*)+caQCH+8=G<Y`GgucxU0Eyj+;JewdGN|aqZc@Ce(&$C4_?g@<?D114S90YtQcL_8{t~Qms<_&Ub@8fB9eBmVEET'
    '+?6J~{-a7o^SM(gMK;~K-)>XE`V+W&$*Sx1$3gi(Hzm<EZk;7Oez|qP{#IUZF+D%Zy1$<}G!waxMp8Me_Hci_JoghI9+#VC#8Yqc;cZ#xp1pnz%E+a=1J?6n'
    ')qWKc_43&3)Yz;#F|!QVK}a;;1wNy?rM}ja1f$x$(O4S|-KG@mdp1{9>%&Ij<=nOySv19^8_IX7psJ|{mU}_gV7olmPPo#44X{D*vJF(rCbC}MKGM!@+@;zJ'
    'lB!ujXL@+bDUfo+`d?<P*Yp5z-QNq8*|pX6<$gz89%s%VO{xJh<8Ib=QRbH~aPu<*mizi`DdbOggRW+j3RF>p2iKQYsrHlLMhj{-#4YUBKFC8E@og!-Pbxls'
    'znx&L3U?VRkAwTG+gJ;)ZK<eyx07eMy9Qf|pHSmp1oAZ4j^kVDJ4o)}qf)L~Zl~I%8=uFtf1Hw+U$~<LDUah8tk17&D~PE<YkS)td*pmvqB=BWH4;9)pc`$L'
    '<J|9LTS_C~;XS++&a1wiof7gWCG)JPY}0-=1OsGJJ`Z>6&Vi|=T%%*%utSP(fwLIIC|){?7igqB+H!&|`t2vD1;Tb0?^a!mI8j<w9FK1nW}mRIy(YW#sRIsB'
    'yf`f+*l^W8Xmkn+Mjl#OG#GpJ4E=833s2ux<D@NIra#%=qx>GRTQl8N4GM1$6qjv0r^Q1#(8Di2M`VXp*?HX*duM1M<R*NE@uZVfjvj=z`x4f|rV9%qU9>?>'
    '>ynGS*B$MF+*z}ELL1`y;#I$n&|ponEjOfl>B+Z~^OpT_6$5<CM%|>nGEdIU@U`=%{*->hdE(rD57PK9$Vpdk80%N8Cvr;DSkBjPjpzbsx%^mPAhfrdhSBC7'
    'IjauVJ2Nl8ati7>O0h%v@-Q@sJv!jw`ym<iayhBb`#LOQd??1^ag5s?y~FXt&b3_lO(1*+w~Dyy#)DZ9<!*MrjJo2|o0agmpMFpLm~QrJi+yk4bYlc9SJ#C!'
    'CpB~4>-Smu@!a|Cr1@6y^#<kQM$9w*V}t@Zf6x-N^6<7lu+9+gX*KHv-&rayThS2z%(PNG7n)q8vERO00!t!V4V%0)+3LD=aQf6tC;O~ulh0)xgM#b_mV~&v'
    'ecyBbG`^y>#dR*Z<Oo{O;&X5eRRR=kv*y={9_+<WWxPoj-wh;A(G(u)w?mXvvx9tMh~hA@$hAy-xXf5W>YX3<YLvwcz?ad@YLosgV~q)RP*$p?ton08AfzCX'
    '&usHNG!Gx9vijPMZVW4pT6gT9<HUU@B|xXe?d>>)D}8A~-LJP+F4#MKH|)}0iH}iH6*r>faOWX|^d99mDeOtAewxPZ;@X`p139}D$*4+{yPX@hs^h~)f9K~`'
    '-B~ISm5rS!pX{i(`Flo>41Q<BP3gNXlpB*M-E(Jn(6P9T-1s^bl_W%Lm^4D*Grb*`eK}0qhJ0_lWGJb!;ubp9jxDv@-r`@!J)F3PX94A?W_-*;;knb<6mdQ)'
    '&ABg*Ig~E1F=|$mb^>CsI0ernC)M8jskeyU5I{=R^$t#4phVSXP_q|8&NG_RcD>yZ=*iU@3rZ<?WI376HyDFfLTheExx+yT`=Uon8MhN;rassGr8x1InRBn9'
    'o}!4RkR<x*u+0(UIDKT&YIy8j#c|!kM6bNS!^gQ52&wK3&P{!yt7z2aEQ}YBGnhdvj|&#q*1(S6a8BopbA%{6`O>6sp5>Yz6c1@TAU0EIJQXf$@5$@8S0kRP'
    'OhwK+r)Y0o)jf~Zt4B)>5B7Udo%hwR=sWAq@|u9?$E(+omB3{{ygm!XaSg9-)n{}vd#S))md?^PM9kS)U`ctJz8*LIF}D(_8*ssf`Rq+TKC7GNT8$JzX+9@&'
    'a_D+<Q;jC&FN^oH(faY}9026i5RRST<6a|NU&Ci9)iEb%jZ@=2=pMnEL{)Q7!`fw-z@#>QY`10jTgWSt60xy~!>Lp$m$$~LY(4d|Jcy&ueXuRE2HJ?Zb^HY<'
    '2g-FUrcp0C6!@N;@mLq!^O9@zOS?rh>{p*+PcrCwyRVch(sDX~^0WF2%q~=f?u2raB5(%5j-IgnQEt<YhSQdN6rlZ}IbOMQ78x*ejLOSK-_BWpSS;~FKc9J0'
    'd~T1xLWTK>joa2Lq?D2YR(6F8RrH5Lm6q3UYYtXkEbs6{L5c_Iz5<?^KxFN-e=Th(`N?;g{RG#-G@gz5$>5ZKUW~G7SK;6VIJmqyhBg+)+ch`BCwZDYyf?tS'
    '4#0i5YuMEqxrt$Zw%+QRqN-B+ek!k5Iq-pt1J7&AdCA8V>2P`Uu;XE<>vAc;a(QJ>uWMGoC!MY_--(#EGMoy$9fnX5<O1Xw+ptkN<R|OUmX5bF3(IkAI#xJ+'
    '`{B-1d#A8>Q;*1xi%$C12oFn^{9K=g<?R!)RaKM$sdG4;D^k>aG7*2B^iEDgF-}oIox{*%9#OA0-w}eaqV~V=@okC>Ii!3X?9UL(-Mne@bz4+vRG#X!R4<t2'
    'B<QsnUlWfZ%`J#cUxb!qS!)<j#kmhWN8n55Z!H87eCx1N@wBAX`DvpnE!2UlyC+LxdZ<063NWJmfskm^*+Buen|lt*cGA)(965E$OBafx?lf$-Bv~TNJ##w_'
    'YWY~g%f>C-8N2&&z-v`WK1{lV8LjTeuv4A>W=HpMXL*lfIG8cN*?EsJZ{LT5xA%G>Y_{j3@-e^BdvECg?%p9(CT;vQyg6q6T7U>zz1H*G7;bt5c+%QvnG{Mh'
    'HYN9UEZ+Ld>f_X!v6n%$-uOQFfaczp8Jo@eb!z#>ovNOlh%eDf+{zeI9O?p!Wxsjemp&37iv3b{j(gCV6oG7TkCS`}q>tVUAr@415{QjZsZ+mtyL&(9Rup8D'
    'x_>X9Yi+o-8$OlY_hKlRj-7~Uxp6yXZ>C)xzOua>`q$g(0_LaT-OF6}3^L?$`smf=%~dJr7q8E~!67odi;o>%rH>OrGiuy?s=R-_EG{LnN`)3g1)tsd*F>7h'
    ')+xT;_PbUBw8<sd_(R3g4t+Ln>v0VJe4Pwn7a_oKnqiNDD^iVH(Y##23GzJXxBmM=W!2dR=aKn#_oKcae_M!Dof2TT2gRur^(tgUKg{o%%&Bv`>ExpfbnUgO'
    'uH(nNy^dZ)dqO|UVUAayj<(;frq{|W>Xm%U6h;<ryprqy)%v!(X*7->+bhDQY>aKW2H2Og9E=y=6dR**gLX}M7mSxt8JoPuWnWFkeP?16_e3$ohJMpc!udb|'
    'k|LG2`Wwa_=X)`^>wL^;KX1`Y`pR^fs@>wMi-~6A$->ZMG9oS={6#|gvNVb+?R(QZZo8Z&1`l(^NaS}mfY+=%s&9w*cwc(Sv!(>}u7;|true(M<+8`v_S`FS'
    '$R{I;TWQlCl_guKdKlCFngfCz`Qm=d^SwO!TpPiJB8f7rz0XL%Ve-=3jy>Ogt<G_+H+JS1;V>MoB&EbyerqTVGBNXbp(vV4#O&eCc`6w%l)4Y5Z5D{SUN+dF'
    'K1qcqmttOCRbCNkBrok!NV0f&{TlXjqU-AI4Cp1jWF%e|&n4BKboG;%F7_aEWP~#@@>clP&Db+5T}p@i5!|_QbvbA}ubd;LrCK;28g7-&$PvJ~uNMDOPXbqK'
    'vub)f#f^=K$~4n%b4C5?V*TE(-IGN$;y%+cx&>CZ@y%|sm|dAe(_2T*o5Tyh9{3Z_HfmA5=at6fz&MO}(d2zCY;&8dkJ2gjJ`E<4g6<)`JvH!=i+L;XW<$M='
    'hJ;|=nF?Je4qiBl{`!1l9W|WK7I4hR>;b?`zdWbaewP;8*H`DzXNp1PrRLSRC7u}J{zBd6u{6JPT0!R92aZqM)rs-0a2GPqstx=D*R9{MxRN>ZZq_fhwl&^W'
    '{7wQ*nrax0!_g@AYEzlYV~i*$BBCs7e32&S{A(mH@9jd?a~F;37e7&wYd0z7^b{F{8j5eao;N(NRq#a&kY%}dG|f6X6q=Jmd5E;jU&G$t9PJn_FJ@oOx|`t;'
    'te~7@i`9r4@pd^Z=YFiZo#BiG@%C#bL8i66&3adCT65a48C7@!E+1))XK>JXR`x}^d8Y2@Hvf@(dHRNlclX{Z&C`K;3!U<6k(?TXtEqOldhbR;bniLE&?^3&'
    'Se+_<!mOpVjBa&!^Q)a$H(rwU2M*rnZF8vbl>DOyX}kBSId{o8%^Qt(ox6@#;n0zNI|aO}2A2FFc(|`o<hdoFZHCi|(m$|#<HnE=d+2L!O4M4}a|xz)yW=yU'
    'FrPX?Qo7OIR+J*o`g;F_=*e$Ip6DL6%Hy}96R1MQPXLVatO6&ypQh>;J*hX4H}kwUSsbcOH2b0fac(c5Q$4^OWPQm1Z)i8C*_gVo)CSkTzVG|WVFP;g<`AW='
    '4^d7eTSwyCv$Vg*6<=XR4|tGv9pin}coCaN)sE(9SxP5Nzq`0%!g*6!(0C-hfEMJe=a`+NBU-9%ZXILnK%UdeWroFoTZ4;zhv=wo<NK{r<0agoe&wPvrv{zO'
    '{_$@IMJwCwYyW<{nYss{`0BX3dwj7;E(gkKv`Kc0sjoQfSA{5UMrW=KgH(SR8s*(-!93>L60SApbFMF?S?;Ds`@(c*Ph#Q#%+|TI`i7i(Tc?xgKxz|OU0bxY'
    'ee-xSrMf)Ef2sR9l`8Y<(BIF}nk}xBG6t4G2R`9nes(%P^+|gYR@bY;38{^4{XU^iHyzqo>hA`U_GECe-#1pX!Rau)LT%yA6Wz7bRzX2IOFIRq>S46>ZzYX8'
    '7E|#ou4+YWavy+i7>{h!gx)6!ot`csamXHmS=OXi$2S%g@m5Fn`$>JV(fHPQ*~aMdZa2P)_<$dLyIF3Q!@o>uvz<MaQh!>}xMwsF9|+#pc%@J@bM%3l-oD@0'
    'TD5oj&xrxAWUcZ6hUUcYF78~YLzRh33JZ8*Lyb}W0ae;i<+&HGjK6hpuvm_{>!Z8pl>Ar<P+i_{t^+PozQ&h7QA?<$fri)$(R94e9@3tG-<Hpo*N2U6Nk?bh'
    'oshCznXI&W<EaG_3mqziJZFdDW{5jZmY?|lIsus+L?!9hQYxge+=kdh2J&~`NTc}-81r>(Nc41X>{STm^wFbuZL;%O8B_4La({v2D*v*^NrY*ZEYQn(^g(>!'
    'ywrdFR*m;l&c$vz)ZP=XD0)vpzTO(_D>v|D{_$zL-s{}eHdY(SbBKe^*Ad-2s`k8B)zRyf@{{1|){DWr{dnB3z~g<x%#C&AMx#F7n7ta&{arWD2h8MaV-Z>G'
    '#^UNYhP|<scB<6$`J=`#Gay;ye5eVVHkPaP=3arEsN@xpP7jl6iEo${|EK~)Yu^7dZ%7=ck4gvI4Jb=azAkzt3&N?6>1qu675mw2By#)#sj*Qj9`|^@DvjFo'
    'v#}TsM~Hyv_jf8$V5b)0O*3n6ck5U+R(ifUD_>x~`m8Tz=^7(CvUx?F8DfUBlLF8g2OW;qrPG{A{Y87d?TPepaV$Z4#Gk-##GFSjfcB5?b5^6Z+eYoz_xem&'
    'l=Ai0G=@vLyuVkCk8bVNedBQ5tePpgQi7R4gOlxYFj9L5r%UQBq--;NczS3lwb8014y_jW9dE>IL!pFH?o5adJ-HObu&(rG#}Q3FH%ud^gVA!;=xoV4J{~RO'
    '&vjTVw%PZlw!Bc!`Se>_tmnl^uKO`OwWrT-YqF~cPd`7TBNe;O2RxhU;vIAj<d7`7DOoCSN4+;$TZn+ZpHg@{JbMegVokoYVoEa6=v=#VUybE|a@bpp1ol{7'
    'N0YT2REW5Ki1o=-AhdW`t5?JNrru0?n`bS6@`-raKWu$5uWDW0!*0Xj-Ux~vT&Bn$FV(}5VNQvRui1+=<_q-xAiCtB<#(d@`U>u@7mR{N!7_!f&INg8<YR^y'
    'C5M&g)ZyBwPY0j+bCK*aVGush8g&pyk9m4VZFZe^T*fS%DNF5|;Ah#;6j2&^$EgpsVwY#4cSQ!3>GrDNn=Lx)3zcMeXxk<%M_U2cFsTvVZVf<ae~+c?;f+ho'
    '`08Xt^u(y1|7<onH&Nek_8nUrD`M-ZO5L_c^j?sSt?RY??%Askrh^8+kwdfp9B^oMdEn<qg~+qhY>JtzjX!V7{hF<%k7IMmd5?Pa4K#iqzB(o;favE$D0IX*'
    'Qg2jllE2!~hk(=@@~vzjwaXnVZz28gJ_)|SyHnfh_0FtcnrLRUKlyVnxnHXeg<-?@$KO3WCB6l2D>7o@4=QcBAOJn5T6{szc!Ulm(moWp@G%VRy@t*}GccwS'
    '%ePCc*``V1t-f+&^m41UUCaa|&oQKRXu!ze*p%c6m^prvUy|a@g;wqJ&~i_+^ekv*HEfoLlb05AQeTcbyK%d-5?8%M{(QxiXI%9cVEEd*N|GRbemAk{;tg5m'
    'aA<q$hhJ<*Bc~w-e7mcwoz6>F%*1!sk?HCE<RG~M({1ZLc50F(-)xdpoInJ;H7CS=_UsUQDWZwp+9rryZeYaD6W_#c_$d=xtep`y@=chLeHt--+tluN9_ThI'
    'C&0$n%_WV$Lq&D`QRU`Yn!|Z@MRPsO7sVfg{}^uT)N|Z&GU&Q6M^D^aW(01wZa>^p(Vb(?>d-G1l{?tPJHxU2Sy|d~uuIQ2HCC(J*^sGHZfWlMwP(Zy99qh?'
    'Xvn~e9UqtI`!u8ms39Nf!gbV6@x73V_pY6){2X=`=j1(MvZj#$Z5hP(8w7>pKrM(_i?;0nJw|R-_0$=bJUu_mDXFWq6j|d#1tymk&+iF$Fi9ZbpeMmy-}vuX'
    '2}ja=aB99L&@OxDB-z~&hbx`+K=#V>leysrVqI#~(`Ow74DBFD+m)Pn1gc$UR}dKkaG*|r?2^B3=4Wtzdf8<=KL~Pp(y2#AX;deu-f0B1I^V~0UTxlhZ`@=n'
    'y(Us^n2W^Pzk{DND*KDjTTPa3``jF;??h8}*V@=y6yg?d+~p27%?EX>Kg*8h!hlBb8Jf<Cshw&2%eBDU71}@_1fdR<5!zqBT3g96O`fbfYPwHbD1#fwV-3dm'
    '=4d!a8qy4X@~E){)h7X`I;f|6I-QlS^HX`Q)cE&Ep|z_CJc40w|Eq@?rE;^`6N%9l*rqOPvuLuCJr+^7;+<w1M$(dYd3Wo;EN6(bBU#v{c@g2cbE`q;7QLnt'
    'WHFn~C&aI3Nql2?^km1<L6jB18hUgZ=UHcV*gv?b{#3fY5z}q4ZMUZ8?(Mm?CWR(>30gxbqwN~Y_6r7V;R#Ifh_FxHXe{CKhL<0m+f=z)g*bHBWy!0X5sE2g'
    '0T2kd3MI&`zs0_n5$hEndr@zhuXczh?H@Tv(BT<8cAYdjw)X>J9_GUS(8&5VZ3uVHFRfK+6wt;0Tu$`xkI#6a@0Bh9ZBH6HWLlzrV(%t-U$dQ*?yGLokc7mo'
    'ktp%h6g6Hj4!?GXMn@j|+qyL^w(q4{vg5(L)jggc>B~b#SAYT^5yaG+H*SSiB_ctYOm85A@<&g>yw?9+hbHaB`%+g3%3Dd!kFOAF(MQ{8yt%P6s?<RZZ@bsh'
    '!m0TcM7h$Nvv~1#o6<e0x4(5DntS8pb@|#&V4_KtL+_$&WD^~6TFP0qlATRf`h8O^M`We&!_)P0%<p4A9xgwwJ-lbP&I0mp9VF`tgP`_+z5A6rau;<puU1Rt'
    '>H%Q@wR-MU*V;2`ZidE|N5XifV^M_m6;Kzp0YK*EM$%q1_q#H@hg$|c_=$=jKUjQH?>v@SGPkxlEym<UyndnGi&EMtLEV0u3k`+ZS9aM0<UE7|UL<#ulRwnJ'
    '^5V5LU3a5Nyymi{SQ;27v8!~FJ9X{=z5DnGZR5`CoL++PG|4Y1Ct%IY)lJn}`Yj&wCM~#`wo7WsUA|ruFAVd>CV)OrDZIc4Q=a*<)<nKxvfjn3byxUoA$Gwn'
    'Z}Vfcc<;nzPkAKtiQVK+LHOen%ZBq>0Zei|Mnu1z?&W-Od{oDCtYKb)N*_h{yOgh;mP~zx45zUQeC??iWP@Y<J&A^u(POsHSNHyvtEAiBuauVi_oxL>WZg!N'
    '{N{l#e#=b1<8x0Dpu+@b;>Ioh5+1Fns~BBTJEkA){KsvhH8cDul*&+XouK3G>o#u=&iZp{HqS5Gct%#zv4#-EWzPNn?ql6^b2g=IcCIaQmR0lS-g!^Vy}zki'
    'kf9ZN3lL4Y3SUnk&ZkIhT;$bWj9#73dO7!P<?Q%U!@tHo3<km`cq&a)^7uQJ8zX@jHtJWqyHU>t={t{Jq!3|AS1nghG@+M2b?&L-z?kcV&L-#U_)2Xys2Y6V'
    '+5@b#w@jQGNvKwvoQLxl#@4>zp|w`?uK$cCB_Q!Qm^FB@4x|ctUQ?~<1c$AGFQhDOs%LhT5Pi(Y$fXkA@2f8aBRVkQVa~m1bh8rWO1WqH?IlpS>qGGR6!+?~'
    'Y8;^r*l}8mz3biayK)+C;p)^W2jYxgDUH(py;_LF?N`s|-O9e(nKa?f0-0zKzm7zcZHzs-ylOF0Rpa$6c-+$u+-SF1gqYmH_Gr=uzxVpGx+`%K?#7K$)Efbl'
    'wd5Ut6(~nHdjE<xB`2w{gT`eg?V;~_dyvCbp{K_e69d2r-E>c@P<5Zc;kN}Rbk*U&pR$HHr+*xDH@S%ChNLhfuc?rCXftdTVudq}s&>xm&lbJli6N(->vY9y'
    'a9{i})!aQi70k=b_FA&i*x%w_uc1inM}FM>WAH+-+;6sWby75i&vlN#fh_@zqcVOa)sZLWRy;T)u3FhOGUfg9Q*TunY>#(_L)g;V!Ve@}-p^Xtd_Zh2&s((@'
    '!dMJD=LJ>b58fmC$?9;`oq7!vSbAnxyFl)VI6jnBZ<(6#m27)})L4zGjtjv2G#O!bxm|_1uvXDKlWmdoxYf{^?`}k;-@H5t`-Lfk8JteL#ak>nIp&tnqIb8#'
    'hmZoGw1LZn$yZD@U3I0R+;ggjel#^%;m2gWt2W(Xq2_nG7w9EZ&mHR6$K$0s6f3q*UbsX{nqXN&n>P6M#l!5rz(#crw-Eet^cxcoFBumXQNTr$^bqRZ0|Y4%'
    'T>sGoykOr4d>B6IV*81Uw^J_+%azum^F1DaM|!P6Rds$p>GN?#Xkf%u`(40-mEXFa>_6b;3$|<kn>`Pj3uJwt%0AZnhF6xDXl_qx>ql{xwC*BcioSBzPDUo|'
    'o(cXdH&<c)Ty!pirF;$-oi-UQ5&T}9PC_!7v^#`Zud2x{3nFKJyT`EGwQASRq1)+4CF=1@EXbW_0FDvg_$;j5r}p01<=%cz5B(W?xwqMJvn%mC5FuWbvOZt4'
    'Z>T*n%$aegdzLRQ9_60j_iNoYL^@kXt~2#8-YyOU8m*6>x?Ofp-I8StoA8~=r*JrZ2e%L#eXjMOfuvQkG-@hqrZJq*(&o4Yzm=3)`}BMiPOequv|z<U5vJy('
    '_d13t^8lW$-HHbqGw>9#eq4oHdrb-uUTMxK=@PlIyn-xt^LouY)xim>9lNP}*A3rWcvK@HS2wZtreWg-m8IUJy8xzlB6uxZuuVN-{&)xniN1!H>ggn6zMl+L'
    'cKp8lM5wKlA0qwY=CcgizfKHPpU#8o6GWK8yH)mpWrZ9G*PaWq#RS~1CK+%tB=ZF@2U&IhC~s+dLI&}E!kV5#-!M%|9pThiutRu2Jv6SO<kKde3YS9MaK`w<'
    'S(_JFN86udmC=zKKIuD&_N@`OE3E4nz96jL{b(z0eV^sBOzgD0?as{8oE89ilTE8Ubh^n{a&DCz>J-QaQ|_|5wpU0MhmeXCf-R5y7KX{pq~;jRvEg`AmEuma'
    '#xrD#4NnMp-9E`Qu2;Qhv)kHk8l6Q`fzLu+$K2QRp#pwOc-R97PB9)0*Wk3C$g?uF?=hDFfI?tIY;SvXSPrJ(yBF1-k^&m1Vt;m8AD|P7YH!`&A%i9DcUCL&'
    'IINbg-1L0qS9^3y>;y?PO6_ZHx8)RYGqK9p7PzwGQ6^6=wgUf@?QvWN)B2NO*Bzr+w-FF^I*{!@ujqClzzdQkrt>p<>0QiPqm~<Nqq%s%Wc%8<3t>ZDC>@sd'
    'D|R3*$~@bfGV>`_EsusP_g+d#Vb;Dc5A9ziIIAe*0DC^8cl+7bz}Hr`wAj==0sP7MEO!B<ypjp`UV<C?I@6GEZM$1qi()aY&KmW4ceWnb)~J~2Gbeua9r{XJ'
    '-C6xapo7_GyezH8MQ&y0qdBwp6m7$JH@e@n;VV>5!S~snF)sGKmLf*R3T{W->2b53GiQ50S4SiE-oR!L^3bZ!(Z^PLSqp7U;f6>uWj;PVS8Uvl#3OuOmHF#V'
    'gDMt@=-W+RA=IdXpNi2gUxh~U{?w|aeo~wrs2HpcM0Z_P%iY;4%GTj;Kc5y3T@D3>(LK!Pbd{lShwTy@YbkQ!2~ZEEQ<$p-qU4d=S?;gb<he$clmz7HVYs;M'
    'KC#6c&{6DnN3YFw(K(kbfxe~Kkc`WxK!1)|debz%%;t14j$-^={_#(q-|a7E|9f8S=J%XRU%=OL%I6#Av+ZeYa1wYc9rU(jNN?W8=Jx@|wj%h|h__!_-yL$h'
    '^R*~T<ltT_62FbOf-3+%@vve&hTbD_Mn2`I@#Qbb<kmzFNtSm2`?PJ({Fq-lwUOVMWrk)mEy<T|6ZnjDtx!1@&A1gTi)M<pwHgH%f`{~lE-SQB4X%QAYopF8'
    'U6u#CXC;mYt;vzPTHa|<3|GW*67Rq-{G1~74b(ZY$8G!pY89=bFFWAoRO7_CKe%$)w1Kp*$?`58J5*#JeXQnO){oZ69uabS98B-bi&;z>`(!iz9+cyDJE=EL'
    '__?**Z~3lA^?(`tpC%4sDozrBs4@@&AyTcmBnOYjr6>c3g>Y}lI^G8j<~>}CW#=omljoz4F|R?~f@`aP3?Hw*&EBoq3gV!8?MDuuYtIV58gA^CjmK|TWWS*v'
    '+(E~^%Xo5IPcG$Llzr8Lp4T4sJ^kALQLN;xD639*Haa7OpwF*p)*4MOW>4;^gm&G)=Dd~m?|&P%r&`aCMx&exnk#xbS~sqROm{9Q@!0t=QSQ|qDUp}o*ZJaW'
    'BQ*0R4nkgfc)Kc>RZ7R&?%5)>(_1q4oZfFI=WJK)f?aL4G2Jl4b-UT>ciDASnvtXvVY&A4wpEqeU8SW_!hqIlhbK*PKiLrX#_}94H&3aY(s5_=<WItZ#e#|h'
    '_2VwE?M=7N;?ND`aS19_R+U+-P6pWg@D%w)KMvAX($u70oMh%sDSmR@$r_cR=dS0$@&m#5BTc5(Pjt~3!i9w#k9JimrN$<usfRk%S$!&v`4*a$W&_tP-S?Gx'
    'BB_t(^2=@Ps@PU`Y^kH&<}G`&ZBg@@g*Hza16FVHx!i|tjwZz@XBJ9_c<S7_ZD8D8uJr{jmo0@ld*&`0&puZS37k*3!e&@Cp?-{7Uk+2dvQ|l1OfO>}SY6=h'
    'H3f9W1;M4R58KxP8}91573R};vBn0M0lr>nN!gRalPA|tv+?r1&PL|BKR&J|RjF#$u1RNp+!Hn{cf+YM*$pFw38^ZZG{SpR`bJyM-}l?)7K`kV#@vgokuyGT'
    '_}zO}EC19Gc|U;0ZWacE<j%(i&m1AOo4kSb>oS9gVlS9e@MaC02pluh`D4GkA7=U9a70f~5eHHl;rPpfi(BJzk)90p$Ir&mz4z1nl(+2h+GJ|%yC+Sj?(pQu'
    ';&pj?K4K;wjDz9zRn6-d(wZARfR)vI*kzANYg?$&RsOZ|<t(T!AlFh0@jNJnaZQgIyh$2dUY?nU8xdJ{ccOL<@iRXi9bJ~J=8J=^({NJ8fx$t&ok~FUM6$t~'
    'GcL^HrIN--zrDBhSx;Zu)jbI?#xHob2hsU_a47RZ<+ZT-t8yMnJ^x|NV^%p2t*&yP#Uk0Mtkd<99+n0S+SCaA1vGW%NCYF|Gu)4TiCYrq?jwaaqVefr(V<V9'
    'XlJvXFmr&kpQFyDw$qgB8aQvdzI<N<_h{_=uJq#ESt=(=G3Ij7G~eO~!FP@D!wG5|%f?R6CBlx6>)?81Ext~4z3I0l*M65h(~sXrzpXzMF}M!IU|U^Xy7*dk'
    'mb7`VmnouMeTz&)a_ysAE5J!*j&`!HL^ThtxZU0keI>}b0sriNdQBjZu&Q3|T!)C>5*BHB+ZS|Uv6-|#wRHxLpc@(sa@RpWoXAY?+<Xjnzg=wJf}(R<mY<k>'
    '=G6~4ZBx55u}{@O{VX2k<#t=St%U7vU>5vxph;OzoKj4<N(V@NdOXt*jM=x5C9h=v-8(-YOaUhh<pl9}QIrBAbX}K1hbzrhvWJ8Y6UWU7%<2loKAS4=p|4dY'
    'Y6C=WHH7W0XR=qsj8*F(=gtXb>=XmlyDk^lfey=vKOvP#bAd_a(2_T4RgaE8;xPBSV@|C8xEw~GHvMETx{n@&B@0T=SnqsKOmx2Q#Ao?}c=KJmmzaYNu`W!<'
    'TQf&uIOx0iq-w`}>oE#q-;Su7Oo9FG;Pt9wgUw`HR*}oe7x&2F-FMqt&V3K262cPj3DAba$~5wb7ce&YdFw=g)pgcsEK8>>+qPPubxM@lYUPv%d_8QR=||9I'
    '-q)aVmhNHw0k*>sI`|#<7_RlO!*q0Gde?^hkfYt1tf#A{i>z<=$cM20;C(A)fZEzx`%91DXL-#U&+TD0zJFfC>VOh3<^rvSFD)L!ItdnV1%B31W%u0iJ^sdE'
    's!i7)EpGX3pjT#CTT|*lwu!G=RG8U5`c(@V)6@qj8-To(0tO6Ml<+IwC*s<eq~gAE85=e5{t|gNK&R(+;}JA9{>IBI#Z)$Wg)r)h4pj%Wr++ZBl?3zSRjMD@'
    '7lwmWi&@qQ^mbIim_w|L9dCO!vRl+L?E~u$oY+J4C55nrARA78&;tdi9cpT12F-yf$FMYvfpTKEX0bkx7D@LrE#Qr8F5DQ(nR)F)KgX1$E8j#7M>x=F1JYt0'
    'V5-%Pej1a6zYF}vBF?3`+Ju_uGavdyRU~yd`g+Uww@u!sb#~;<^_r(JT%_-=`XtXT1u?Qz8!_yDZyw9#UVAcMMM*T<i{NtWk=)(_i-CDXpHfBWk0z=M$+X^4'
    'Cdi=PmaC7TcRwKB_23w@3$}O*z|bg-E1l1%^3xzCy)xdo>8oPIJ=tHas?-4@-NoY6r>s;=_LWV#C#*pEu-44)>ELQbtA3renG^K%i@R}&&9T=#iAeFSs78@Z'
    'p-*kzcnnIV@*K%cfBCh(-jvTe&Pn>YTxSDxO9bL5=v6zBbimA?JkindPpAKKOnt!1=tOSFpLi?T)e_sgOd8-M>Q^iB@LF4ORxujJ5MKD@$~8KB*@_w*x<~Q-'
    '9^joL`>31;c{lF;+7^ztdCNbU4}Co9Kmmpps{txK%f*rZY!;Lk?{0<B1o${4d8Nkk7mPV3?}jkhTe$IVZYyEAy9R3gx7uwnKS_h5wz``WQLiTXF4E^Jlz}h7'
    'J!k3wZf*Gh%x3ENsDD5FTe+JMEpRt(t=!dC`H5PVtXQb7Bm2woYQ5#ief>1oVFI+4N}Js)_rNL*D-KRQ#6g*Uzjcn2HY=HIS;nBRqrgI3IS$!r+Ba?dU@7T7'
    'tSv6`r)(atZKQK&9$-UI`~2ZT+iVlcOe9{RxxDJOM;fAk55=Uo4xZZ%v(p|lW4EstyNNi|nyNK!bllZza-%0G^tYP5mT1sG-?gle&u2a;oT?Z*9~1gt>A@Ux'
    'trTU=OW}>yBX4)PDkJ!l>?1Ltp_kPYJxWQo0+T+cQO?Vw!+9Z=`kV0j#=EVh^}>d;15YH9m_xPCC<u`;`(Cc=_WZ1b)~?-Bajse^aksl!Xq|S!cjxR>{yfe&'
    'cRUJZt_*o&h1?32lLnt9A-k@KUYi{gL+h}DI`z)89uYa@eP@$XkY@e+XAL-%mTCIYHulP?=E7a`Qfxf78@!Tdh!9H~)+Tj{Ta}|(&$BzKNd|j&Th98|B`C@d'
    'wB~gkFh3R@aYF8uXHj_0J7akTI1oR@)`_0iEIxb$8xu+jG0vO!xmH~R!45l}_z2x~sq#uWqG_;)tNCDLZ!-aUqY41|f=;tS4!Iusoi{pR=Vmu<lawWoA3mN7'
    '`|DVkW$?@jPtGiB4KaGTTMZPJtb=b|jv{n%xq%Ov>J@Mb6s;b-;^5ooS2M@PA}}yfIa%{%);z8uv$Gt3!|&u>BJ*d`utrS#rkv-nBB3AJbg7qpxJu6|X(8RX'
    'EU|vWK-W1sprcR!xTy;f=d3><;tyd6%gc@RX0+M)-dRD~fdMGDpMu8YebL+h=%I7ZrjN%gmQ`j?DxUnZN6hxUe$)Lgc3$reqPKFB{l0A_^h7j;l%1GR=5UKo'
    '#a}=J!w0q#oNj6(13H_$v`p&tMbE1s(dkI_ngKEax-Iej8OmMFdLpbZO6TO0l<S*u^|S9Xs&%|9O1s}hgs-&QA{R?(USE`Fn`bFbB53OioH($a^A_BAHS}X@'
    '+zom%sUYS`2u#Y6rtK!m2@%eVU~pF7<Yktp7Uysic0Z^MWr8wVkK(&kqg$8Eeqxldr`ZT>6PG9m2TFOTFTRRpHb$J0B;|*HUZdt~8q6A{ZZ-_sxlJh7d9qAF'
    'N`HTPYrXxlfs@St?&HQlU-H+H+?0BIG$OBD<-!=J#ijJRZg%&NH>c+I*(*@&++pvnPUmp6i=Rd%IltQWBdqZn`?^(3{O8dH(5u)&81T9mD)o2$!S~4#Qd=)O'
    'E#h@w5WAC1KO|t5?VIiQ=aBTQEvJMPZ{Of798>|i*p`s~eF!^`L(<rAlP>RsyR|E{t&dYoo9Y-o8t!$iT3A8M_Af!%1#^puoA5AvEW5z3i}~7&jIYU&Zq}ZU'
    '8K128!$UVsEyT$;5gJLq<4OHvx_PRn`FPRQ1+yFwXRxWz^*Tfrg@n-iv1&EmQdoJt7@1d#!;-00q$=4*2m*8B4;X)0mSQq-GGWmg`>5T5!eHNjs!cXgD*&nE'
    ')h_$~VQj`QF~l*kwL*j8d?Fu*%)6}n+?peA!66-|P2>`{)asOO4*f-WGkrk^VaRUIMeS<sN9Fsr!tuf1a9ER3>Zg%Aq}AhLwHwjCsW00<TCtJbhyt3#rqP?-'
    'OEIw-$?x0t{yr{;z18^0?xN&x&-7YqzJ<ei>N&fEeN;Y7^Hj?_2&3>X_}FxkX;s)CC>KsEAXh$EMD6a#*US3Xi}Q*SmYz-J{!YOebolU#@3HTIwQv!gIf~iV'
    'c38t=p43G+(skA6-vmJ1klk~bF6IU@0&0uyWkBiOPqzQewAvYNYQiIsNu$<fC~o++2b;rt2r~CM-EH9>jHm0M-I6E2Dy(d@CN+2wszHN8Ct%BqwvBUQQ!CDd'
    'o7OHCdaT~lwtv1qYs}fdkE%UiI#odTb~1r4EZL81IXiQ|<MUN>hi9Gr4d~l`N-j$8t<JiEf^AHO#i`~sZeL<C?}dOd3XkGqDi8Yj;wP!HfhV<I7Ruqlp7MYz'
    'Uz+LNhx;8oSa^5oV%j{912BjOGALx!_-tP0!dWM)UxfWI!JbX(-#WczPS|3Gc;v+qlxW!N*LGyjSob<J@FJYoDSeSdm`%7zb58Z_4nb0MsR8zO++YXANVUA^'
    'cV<p~bQ6S{yQ$?5b6FhT-08MeKDf4320C|oT|bBGr&U`+3mvhHrCTNLx9UDCaHzH%4f{$q0eWj^bJu9$9=@Nx5tKIknH7TZ@}&_Y486fuW&^~%2SW^O>hy#+'
    'H!_gyQu^4g+9@_6OP{5h>-ZC9guNp)UG>S-8teH^`u$b3w$bxr?qP2;eh;eEO68-D^E;|qQ**NYEc$4pWFmukGcf=LzQnPHYbTiQ@#I(S{MK|vD>H{ER~bh2'
    'TgN9n!J#H!LhzvKNzj>q8@(Zz=A4bpTgR9li|npv<whI%e1%5#wUf;tSg5RU`XA=ry{m0qX&nCltaZMFOD~Bbp-H$0OiLl9v_L4Nx1FY`lQ`fK;xtZxK<Q`y'
    '%|(*sTcCUI=e+M;=M=}5Mx)VaG&35F7B;d!%x^c}x*tD(dA+{3xY9Z|k8Z9vcHeyN?R3^x7M7olkC*+W+4Gk_?W4_?#ontoqs7Oi_U`Rc@7M0L!;{TYsr~fl'
    'r^>IT*_YSnovSZTv&A<{TUV!RrOTzt;n8SuwP4M@_%T=M{4RX>QJFjRAAdP+RrV);eS5TaU3<3vZ0X0w?a}9()&BeD-qMeL*Z#fqwB2f6on1WHd$sgsVy}6X'
    'Sy=kI?flZ(?4-8$`>yo<V5Rxy>8JD4-stvA@#K2p=2!pQa`iZ0d@(uvbz?rBRQKNQ-!2u8KY#eP_tQSepKg?vZx0S$ynb}~{mtq1?XS1Tn;&1Uy|!MR>_2_G'
    '(DqIipS~D>c;%lx@e3O_rOLwDt7nTh?(6GM-`kVj+oz{<v(>jNyUm}k*Eg@PULS*Qd~CmY{ByKcxgM|mm}EcxoNR(PdNDreS~r)?{O-;8(bfCe?H@P2OMm#G'
    'w0?B@es;BRd)PWU*xQ}keEe=Lzxnpb?DgaJ_iCrTVK*Ny-gpOFAJ_a5Xar|B?+O>kXV<IWceB6Ui`wKx?PIrhSzDd#{PhXU(CXgn)%D?V{@KRS!R_zP#b5c|'
    'x77~|{k_TR+WWcpzd)?K=&dfT6kpvIz8`pxMxS3VtZ%=q+%2E{>U(GH*Bklm{^|bko9%n8$A#nD@2^j1^M_|Y+ST7bZ(dnz?)#2y?w`MX11r<h;>FdeJvTcx'
    'kKSyZEmUuwzW!KStL?p;eYSGjy87uXSg)O(55KOL&Ce}w>0;^SY~kC&w>RIsv%&UhZD7u=ynWLCx$^AYucyDCp4wkN%oPq+9)GHAZ!NV-cJ0Zx(@!54j@tW`'
    'pYI9>U%vgSbXxlhdyC`ktHPs`7hlYqldD7P_m}F<YwP>^PP^JaoNOJh<lWNb=kE8y$<l|5!=oR!g@v0fYy3T5INpC{j%$yLqu*QY_Ncn+y?n9r@l$u>rd7Q@'
    '?LK>1`o8i0{r-a4&Q`bm>gd^DPlt!E4i}D#=bu&<_qJ{y?Y+O)T+83Sc0N2?9%Rqf^7|{MTiSp7q<X&c=&z4wTfK$x=e6!esk6V~yq+w5di;HRad&XDV*Yhf'
    'I^CZe*EZgK-@m^8{<6F9x%R&G`0?CoE8FtlK0f?VwfD|Xiq<AZoa}q!;o|J~M}K`@|M_~qvbgi{U{D>Jdxz%JH#c_iduQ+6<8|-Hlg+<=<h$8Ne*Wt0`=;}1'
    '>B@h!x#8Zt`CQ%p_Mx3$xVzdceVDB8UGM)`^-J$oN-GC<vmf@H_T1v*ANJ=*R`!{<TRXk`&~oSYe>^EIfdJmwvx^J2hojR+zsy$`oyptR7f(jjr@i-&-d;c6'
    'Y`r&MeW*Um{>To#eVVJ(x;NSO+4(sC^k`{kE?@cfv$lKu!#P;FoOS!VtJ&Y)`<?X{3)Rb)i>6uXcP3B!t>M;Eb!B;O^)g@F035!o&t9C^Px3#S-sGA6t$(@h'
    '_g-H+PY#BaAD2I$)n4vdx3ACkFHa`5-ObzEACCK1d+@&fWxTRDSX-$q_YO{Bt<Sz&>n^zOJ@4rETJPe;FXwYUzyAGke*EUi@O*gdc1x9$?X5>oI)~?z?!o%!'
    '-^VXrSp64EJ%8?F|B?S`E`Q?R6wZG5H)gN)+TK2VXI6i{-~96AZFBZ#bAR!qy;fcKmgdg)4=<PdM{B*)#j`oQ4EJ+?YrN;5UNzg3<sZMl&+bfW=iAPwh1TM?'
    '7r#I6nw`h1PmdQ~eSG|+TD&TCpX_eWefxIzz4`8E@p|s#?Bm&UuYLLPF1z9l-c~zj*IREtfBtxRcC@tmY2SHwc>ZRRZ$Ei=QMrbJI)2n2jl15HA9f`>_qp(^'
    'U#Wc@uN6MMIDFQBvop86bk%!wx$tRm$=vns2JTv`l0E$V>8xqG3!D3UFE5YIW|v0CPhNJn{`zdW8;|y$<fr}fw01mcy?nR!<mmkU&UJQa?q>5>Gy8F|u)lh|'
    'zG_yNybr54y~UgD((TLf>dnWePhOfIK41Q5&CQl>&20Yr+~~*h+qsvE_U>_S<z&zQSi+@z^V4MY(dFvh=|XnnviRZqkD>kk<zn&e*0Y-Xy_UVIE$tpWS-qZn'
    'v+!=UcCc6It^L^h`DWC9w|a2C{P=p#St#v2dHdvjYrOem(ajE*KYUpK{&A^Q`*rAmDsR6&I-Xs7<BqPkUw2CHPFA1hJ$wIMGrxB8(%tt@9&dkpJo)|Y#yr2W'
    'f7F&f%-LJtwm17<uCK=5o@Iw0YYUgZZl86EgUzS*_3FFA;?Mq(_j38**~Lx&)a|@kU%h_3zq9WzEj=w3xAWDT^P_KTx3|l?zdM)P`}r>?mHz0_=FRu<^7&t{'
    'KV|<q{Ix$h`LgMr9iBgXz2Sdu7JIYR@7~VY_*?V+`~J<&_~q60&4PP-`}31o`|I-a#}nt{qc>e==Y6Y_KRmVySB2kuoqYGvkNlgtvqOK*pMCW4>YH_YGx+j)'
    '=XAICZR>db*;{Yv=Je&T@^p4GdUxr*z8j1-j-IW&yvzS8UOhei?SKFF`^vo7EcLeYXKxoizI|LffA;C|mru?2i!UzTI5$6bX2<W`-*cZ%zn|PJeXx(lRp-}T'
    'ZTz#aIPA6F-ZfvlA2$w8UaStD*<eGx?rxZ!r-O~9_wUxOcQ>;OH}2%u_QKBcJE#BZxG+8&G)JTL>vikfo6CcZ?drR%<vL&dtM^NGtM|D0t#!A*_H_1%cmASv'
    'I@{U2{cTQGcZ;>{;+xV+^|O7wXZ3&Ye>f?<Hdp5I*N;B@`n5JZTrb{s_fGR?_V8lk;NbJpyPt&*<EIz)`O~f1?(SuA|8VcKTeFV7fBEa#)6wUjH`ZvW)%&v9'
    '^Saf&h3^NQH*e2(_pZ-hefaC>;9&J^@$jf(t?t-`@mkiK6urvt$(Pb?^~L6Ce|#{$+56R7IQ~@HsSckVuI!DUYz+o)SAG^hF2CMCY%Ps0+AF`aFFM`3z47ny'
    '@Mt!B>2x0N)RxazU%u@uoxJ$?{pzo5Z`R$J{rLMNd-Y^{eEH-<W%p$}W18lF|I<9KeyCMWtXsD~%AT9$dh@tgSZ(fX)wb#xyFGHfzMpB--G<TihK6gneZ%ee'
    '{OddikN8HfGxWwI2dd1wBj>`;ns?X+em;3qJyNZW#)F=d9o94cnKyvaW_c*8W*GJ`3Re^aa2=<oeF5+%m0E4@a2LR4&g_1tY4_aIex_{HhGQpZWUd^i(;PYj'
    '+Z_fkeW%xJ_8hwtylRa*r_QK(I<|-S_O;#f@%7O2E@Cg+J^NzNL?FKQwgd2*{>W>eYcEI6@WSoe(3<;m>~?G<srI=$^!lUbaID@z5C8k0$42GzQE9PQHo9Py'
    'cZ|`MmmhdNw>>f1XP(=Jnt=SU51+2w(HWGwbd0Mrujk}Pj(uUAIlWFE$O*LUb^Lh*SUYo!?zq>>cioXO8aj>vv@+~ok1JzAdhHuy-!Z&?Zvr2N{wR-aBlV3h'
    'TgQjZlUnt-Vzj++e?(wEF02_y^&V8507iL#;Iv&Bf*Zum8$$Ez+?j$ZHv&{V_-AMk+_rbo0tykY%@ey63(e~O4zUc3YBuv~>s{seO9sd#p3JgQ$Qhvz#~%*2'
    '-!xB-s<ni#ueXj5D#s_ygRSFtm81fD+m+__ab@d(8cis0RH-$$w_aD0KJESW*H&7+lY?rt_GYh=_B|jfeq5lBT2~Uf9Qm5m?{JZ{&WB5-Q6O9@PKL<$1X_ek'
    'q!1)rD1j=GUc?ELP#}Re@lq+|i5E<vP`qG_NC`#abcz>BCRMy#m|9C%D1vL8S_uUbs1+}jLalhg6l%o_#;BE0Bu=e(p=4^s%Y~`6jD-{maXN)QB~VEJo<bYF'
    'ND5W-A~AY|KE^4be@>=>ULxH4Vv)WFKobZM{+L99P>D1mgbJmRAyg<%i16nGQiKYm5F=D3OpX;S5Uv&{Nc?*OO=5*o$Pz1;LYY{(7;)ky;`E7?NhVROSeQzy'
    'SVnslBGFpH$1r^oO2mn?5HA#`OadgGEX6{?_YhH*;{{?A;VBX>6q!UN(%G6H*GkRW)~o$WSY-(pUb}a-TYHF*UwepbTbn-l*Y2ARYY$+Cwf_M#to;kjuy!9W'
    'tUZ7i*6w44HR6Ph(>0o8%?z_%%XfyCq}=BGku!jQ?2%)Z|N9>U{&TwqzO<~8c!B?oh7;`<{?{B{S{k5wrVGX=+GWK&+HIjvgPuKchG0@P!Z4^^FtW~_Nv2_C'
    '0lj`F+wFPwC=1~0nG3IvU(DQsnKNQgFKnndf)+Dw|I+D?yx|0Ye0o#aszD_)Xv?{7JA;u?p+8W!JPnOQXf#BLO{=)LNR~<88*$-zu*$NTjy+k<m>MuL2rV`w'
    'vrQ~R|LFA2jJ&IUCU<*h<}%}c59~6q1lf?x)f=V(b|(C(mrD%|f3SX<edo%ea`R;9gvQ+5unHO$+#Tn7;0%F0R)$TT4E9GrG90k#j0_k`nOHqx@>($ynL14<'
    '<cfuY83PwFlC<IlGrbihp|tYhGV#hp_=bf>a%7~I7gtk8s<aXwsxTU*q&A?6-pJ4yjfZ_5EZ3&)p^dm$YF3XbhhX<x^?K&jhcC^e<Lb_bZIYGDmN}!i(8w97'
    'Ul$7W^`x@DA9)Q^2b~bjA+$2G2M#+UcwjE=-q`W8vVW>fz0j~aZX0J)@FvIe#;W&RA9&Lw--gHFf*v5%$*Uo2LI?K_j`pn!``l^Tr!e2LqWK()6-$Vh-0ZA!'
    'f0&}yeEZDyeb=Awxb|t^^G9ymuLo|3q2ss5PSY6<y&;GYWM-CF+>Snf+Frlwo{op~i{`5Aby!5PpU9%t(*bC#H2?&IUt+8o3csErL`3OZl7S%T%Jt0A*2zhx'
    'kt6Sq4=><R$SZi}wV9^Y(bjS0ux3$5nd0K{&j}#Atiipv=V7A3G-~2JYI<G0rnzaY6jvic^U?)@)cgqlh8k(2n2t+5u>!zUF>_&#Xm?M|FywLH9r;#0vR06<'
    'FE{YWyXW-BKxdeTSwv$V-n!(fF(XJSaP#(H;K1Ti&+Ht-y4m2ao`LMOJ3s6;5*dKx2wKathaHo|2>piDCF`0j<K)0bP!^;Q7=RkZ$tD?qUlhwxKG2~IhTadS'
    'J#so$m_$wWfl$tJYlLhf9>LOxa)@OKx;}FX4v8;%RWOAc6@DOPg-kj@0wosTEHtLKIq!SJQ5M!xt7l)dI=11J^E^sJx9#`@%c~a~0BhE(t95S5^!ghj#F(>;'
    'Vn}SusVp3s`Qp-|ap85`uG?leU)k6?yKp+jD`YIAdgBb&jlsCpbK6GS9@s6n2R!EZMtkUVfEFF2<@CHOayaf>xTB%#8oRymO~<=5P8`rjj2bq3On4D9y|YhG'
    'dk*mKsoQr9n2k`UH3qfC&ly_-yM5;5OY?<!k_{gY_iD|<6YF-S+3edFPO~{vp1CZoHbHx6A}=)occ(W49OPU(?QG_;adNctIlm7i?)y%DuLCR%eRGCo4ffYQ'
    '^!<7?v~f@+KF^JFddNHdOLyq?FQBHcqX*9&XWj4}$2hFkK+ByUU61C!_Ge~hD%SwY=r}wKE)ELKx91(FZBL-eh26)2g3*<&c8A_YVvEK3h0^>Az&-KC!?r_Z'
    'fMdoz7(QoyFfmTvY?YRljaGZrURqpTS#!FDQhUX*mls>Bt%Ze!&a%C>vfM4eo2B;R+TvPqajjD*b{Cfyx}}9yyX`p3OA8LPaEQwt;5-;2<~f5|*El}h%^A|A'
    'js5p}Ff{1-cTj%OJ3!TNQ3kbp;||OWBE#4I*M8-2cki&${0L^kUiHwhj2Z3_d_1XsINnB$o$!Y*|FjF#;5G=d6M%O6wU2B*L%PCDnWxO{3=CIih7Haca+)_M'
    'uG8x@L9c<=C3t&bUx(f;!aE`hs1q|}b_Ydf$S|Gp`lp`TKb?{L0y)w4_SW%nRW`2LE<L>Mh3RcCPHDSVJ=m&MqiruGx4oLs_G-B8;?%ZL9aK%9)Q-14y{a4^'
    'e}OL=$&=eI77`k#ms;zkhqr!E*{>eP27L8T8ZZ5=A-_ZR+dAAk*xJ__aJO1LsSqLBAf9nhi4gv1IBw${hBq_Y)#}kqj*7=|TudH_vw#w?B6R>5LaOZU&IJ5d'
    '{X~RNO)tiqhK0NK;kYuB$`=Wva2C)(Yx-bs|6S1b$(u^$NbmO2AGW<5ZhK*B+n=h{{TVd~YPGhEx)1<4H5+qkZsbC&nv<-PV=CrEk8%P!{C!<HuI=sb{Z%=h'
    'X<$3-|7admKUVY+Kdc_t-T+ov=y1MhDvE$vAYTV>D?kGrq%4eULB0J{5pVPIHFb>K6|A3u(DVJ~$nAlJL#kQRcW*%H6#!;tUc-6;0=e%D^KEYke+(*Y*yK;3'
    'ojrtv9t7j?(@6y+ddC^gliWrSXLhd(oeE$Z&z~D5{w9=%dX@_1ktgMonKS5Z{7q0UT*hpuuDO1K_G!esC)#J10+cba6SvvxoH1d;O+2FYHkDifRl#0w!g2;}'
    'wujyzX8;rC3~a@34xAzKq-?z10kY6CQ^%r>5K4jvXbjHXeuvn6f9nwVPWyuO;0v{+y{7gZIROv@?c){b^`K)lM;?FXZD}1SXlqV;JaR7`(1k>C78u53gJ6Ti'
    'La@9k46NWAs-OmlXCbNPDE(09ZFlNQ<TY65FY0aM%<Q>c#~;{zvXzj}^Tm{^S;S$EzJz5jD5$_M#%zS}dP`kr2&0I5)_@^A31a0XI^hwu`|gF^%km!@R5^+^'
    '45AR$b^d(sK-zUpd^L2W7yuUGhQedoP8-q)q0<MmO9NR5(_tDb*i$)0(Qw$bFKxGHw|Y)eIkXL7*qR8g+4A~h9nFByY~3}bxtYb^AXYlpnlyr6z)2S9lrSf`'
    '0!YC*c!QQ8Ow^8Z9mpPF8?0biMxh+wBSr>m*Jl{UOnA`v6WNwCjXHt=nbVNq;Mv$PdJbc#$_X15eFlMybw=skLT%WWeM?3)j3e}tyh>P&%V3MK;xW8K)xyM9'
    'zTGU?kC!loqXgd*1<*D_D5##-k@`(Z{aI?Sv2L6Wy(_SEWmll!z=jIALI48<qjGfy;*;nn+N{sGK`The4GSS?9ZN1K-43^RW@z}5OCvqBC8B=`%R?s%e{*D>'
    '=ZwBpRHM<qtm8|h9XtmXIxM0fTlyg|Bm3M*gVT*y-!S@dW~4b2Z98vaO932-QkX~3tEE1M=z#jH!W3xLo3L@q#=2lcecW@xj@Q@9q$MmzOMVj#_qIElSm>}0'
    'SmtQx;VNmsL=aQ-IkL#tj4!~?8^Bd|&+UM9?Dl%jsofJ_P^|!c0{8<A!M>MAhrB+U(edp1Zr>l-{k9`rHN=?Y+{f?yGDc$l?G0c=g-@j*sD)lHYnu2`&69u3'
    'rzxHSzY8?%P5>MfMF$oAEjHB1Y7M1Ky|2NL1F|6HbnQ?dc4(=CE$QFuN{_(*`cR~gMY`9(v>iqb9wtE%LDOsj=Uo39m{U{KP@?jON$7*Ap%Enj{`c58@Gc$n'
    'I{*)iJY&DQ{jRbj^hThc-RpT*P6w7bmfCH*Z@`Lw)raEnj<;=eaL8?W*1ZTyj!<i1K~zO9WNTO6xYsdYaiz6@M9&Zd-G<I3sH8f?8j2uq;IO;aH?pK$<%~~T'
    'waRhMa7OKU6955sG8-ahdN(v+_X+td4})pOIYu98nAK>=oXnKd%3;Gem?Y#03lM7E3H+bs8u#o3Xr=dT==fgm(lJ^N(t)J0=m>>4&SRM1gdza(6SYC1fVM9o'
    '+PEo0E4U&1XXNur^9Mrv4yffcuvhj3CjJ$MDMAsO3<Qik^txDHLhPbV5gk+?n;DJ-b|7Lr#t_?ux)&UrD8?A~Npy&W$hbdr?DiR|A?yenoq4_!8nA%Y=&9Ce'
    'EoMU8cF6LaHgkV40|*@}ScvfVj5af+PZ$^jr#LOoxKM}?+9-I$4d-DY@;*iU>;Iuw&Fzn!2)-Ur2eqhcv?4>o98?B>e38X>YUfMmUE)NfK2&%6S&+U6%#0yS'
    'Wi}I0M%Ze3rG_HwE7lEHOX+3mMB3Ya_u>C;cmWuyFT9T6ie9>}0{Z{e!c){`G-((k0Sg`WQRthNu^>#PaCee8A})$g9H)b-+a>L31{{g6L8YXS;2}B8Vc3Cd'
    'JMPeFk3aylCI$(`bsgFWg+(95DQ)TD?Doc|XJVZ<)S8Biu@n%RtW;(~d~$?%AWR>@XR5OK=X8iP7E`cDkSFPc50TpYTicZgul-x>@z~fRQ_vv$4;Q&|AdP9Y'
    'ys$^@GyFB~d+qjk;5xJdvUxdgYzcW98blQGE=OfUQLH?}rDk$saBTy3wn+$&&Y)-umelqcuGBb-sLcpl3|U_wVgNhzdI58cykM~y*rPMCw-X{*HX=a8hM6#}'
    '!yjpN541qm2oPU0UJgGJYq9lh;)qFmotPkGjK}Lso19h8KEVr0B?#(7lb~oOh{42#92G>(<G|I?-*E3dN9uNl-k=O~4;H>tuMdL&>$nhf`Y5a$Udw@n8lSg?'
    '+z$`O-;<MnQ<&Yi#6>$Bkqc1^%lv1M+vDL7>1EM67?o0LN&J%qRe&^8yO6wu{t?<qW}^lx)qH$_9+50Or%Q0Ql9NT}W1|8xW-=nNMY6!S7-QUzALyX?fW|6I'
    'J2WOq7{QC7^K%Sq6qdC|5+K*{02*tbfx5?9v!x_l`9T8xu=bAxI(lT21v+{%@uLtY<o~^2+mI3)YelTjlp4{6o(6|q(gpL+R!j!KPHJSXV$|W3BEs%*gWo?6'
    'WQ-*!aoJ?ypDORgfSM1Zb3NiBZ`@NYu@2CHy)QaPK(|M>a{6;Ua^W``u|BHun%6smh<)lHA<=n(j_|y|MECwjCh`@K#Jg&;on;wWt&v0rdazTYVHW}djHJ+j'
    '=X8Jx5{Ep&fJP~xe4<yrfvX1gFlpTgMnLz1H-u<S!e^$DORO=+2t9x=-)tR!q>Z)Ms3kMz!}yN5R>$d~Q#Ax2#`clQ4`xIGIhD0Q3~J<!ZoDQ9_+z8WtV|Vs'
    ';b#D)^<vzE>0@YpH|#FVCnEwimjn}51v2{)E~%k(K2nFZiJMQLGPh}ov5nUFbUqGANalMcohBYZxFvrh$q3Tx7(+eFhF}*|*WC+Hok7zy1bE|?2>UgIEq~24'
    '?u?mfAhTisXi#KTZBP(GPAM={2>yXrQ=vwPY}^K9_?n4)<QAra(<v`;)ZQTka~*@Z(T~H{#u+*CQ=pm;(|@=@D`{#+oEM4Gq7W_=wgvSWlH-;Vw6%vx?P<#<'
    '?;WYQ`W`@4_J^=N%Ky7wOEZb93OpKMFv)<41X`qtOcnC*KV8n*;}f#S^x%sGyDV;3ZM8>yT6$=FhY9dKM}Ovu@}czI$SxSP08-eR52eldsCtmHu(8DubTY9R'
    'M}HW+*<E@7v3K@%BV?BP;{$ZZ$HuXP4t1Zm`u&`N$LZmZb1@j<mcKW6j{AD#UD)xU++no_P_PcjR^F!;8`xo+a>_8@!{t#NA2xr|$n)yM-u_OLVx`LeM9WUY'
    ';#Ng$P#bp-#Yl!R{U0MGo4I?)tPLAX516pgk$kYy-F>jaoiedyfY!ZpI@VrHSx=+Kc6EQhvR!LxGUWf9ItVf%L-cTq#sfQ>R24T5gMH`t0uYsz4<OLiapix-'
    'FnVyx!>ACdF=fzczno&M*@pGSb{+;KN%XXBQcH^k5fe|43KxwDc5G<(Pn~SC;|vR3-&ZJg{|_ekbt6$1Nujwnj4!H>(u{@l9i)q1pmxNgw&ECJ`3=y+p?NF;'
    '&+z8Kt)YXMs^zhoX*>m^@lmoLD;YqN`V)3#gm^1lFvSa(Fc2X@`w68dg*Rn#^2h-m*+NPmR*vxi0v{g>zVT@T4E-;zmO=+8%Erl=Hz=$X){GvkzIh)HLF75y'
    '<!s_Zsh-j9c|IB!$h3Xh@TOpVaU{aM7<fZm&qWMA9y^0yBKp4TUgMGuFOCm)IV%6c1DmXko_v6W$z;f0^Tz{(<8)+PzaThai3=5;h*<~4@VxI`^$qONm_FGp'
    ';6`9c8PrcZv~6!N5ttbr#~I*n@oD5<NTiK{Gwe1g+Rzz(?Vr@Pj%zvN_1@vuKDsehFw%OZxC*n5gZ6#kZ9Oc)G=3SkU+Hks*G$g%O2?G=iFXRcGwxle$HN*w'
    'k{5~}g(b&7lyDRv_jdUqP%re~V%3#ZD?9vz0#iK2)|RgsV4l5N<p8_HF{&~mnKnu3jZo4lY^2@8Ex8YUHALBu=&i2csU0ayaMw=BI6g@BBWIjD6Oa#1*B<vq'
    ';?!Fxk_ZZsz|hN?5uJ_zv5X-{4V1S>qhY)OQxA{BSW-XBhv#IY9Ck$B!W?ls4l*Ij<p3N2Get@&1H=A|diHCEMCS=qMv4{-7#{pJLtu`a;SL(FIis}5ubqMG'
    'dmZNlgo=;vS4su55k&fAV>pnM%wnK_X_1TTo@CpF9_y6<no)l00Y*=E0HNz*;dyECIn*`e$tvMZ`<f9=x9x%0LkacwYewIy;qIx84hp#Tg~tmKOsEbb`hccu'
    'l?nqr@cfjZlNt0I+utyXC;$Xl_;pW5T@lPBH$0wGO{3>txFgju!AN1cLXDhgM=^zzW=%Q?jOQG+(6VjsVqgzx0~v*jl6+KlT}mWA3db=*cK@9Aw_Q41<cdu('
    '=UN;vQo&`uV~=#oL%T>fK3R!$QshRlk1lSl6dlfouGSGsI0i3!dtNp!C97T<B5YMgdLYfuk+Z(?aeSEbxe#dKh6mumv}t=67q}^+;@|p_=~@?Yb_nOII5mlV'
    's7o2xfJrbLDnvn?RHk7z>g7KAL+e3#>OeElQp84ApMqiY+U`gKIQTD!yM#5W?})Jt1t7{U;9&t;7V)bjIUqvoEMj5-UQ~dz#VLj*Ng-02x<ct8{JkrYa1NtY'
    'MXYZCz7e!2>81i`MN#!$!%p;<uv5Xd)QmV&E9%N}S~Dt7!OyYX8KSxwZ!)orXnru16qA&c@9Qi!plD9~LQ9^ZXZ0FEK{IDWKZrV}4ps}S6`iJ9@R~b~k&arl'
    'Nwh*_igXb@Gs+@uz-SCBoO}p)+=oR3+iV0{HZvc#DT`}Di}q|Kk;Eom$e;+u6d}X{NEM7ErVx94akh}C!O}+ylr|~8isQUcI37SC$|qtGU;?EAW)lK|X)k^R'
    'FsN)OXbK4^gQp2xSV(gLH6A40alT5@!n{{vyZpd0NDtmsW(jI-a*H*O`dT2k5@~lAHTn|PCaH!B-25|8dexdV4X*?_CgO}A&??n3F2<m_w9qMr^+K&i#_6BR'
    '>+*dDplB-+DJ?Mwkf|3Ma%VceFMSV<pMw<-{kot)Om`H-poV%b^^BlBJaToP9)4F&+^@l9NAdm!*o0b7imE51LZ@uwOye2q1+LSv4kR_d3C$xhv&p2dml~v)'
    'ndTp0()aqPx154DMaY2k2OS0#Kn)?G^vGxf!5?yx5Q9u(cP^-L2KI_yVyAeTKY-^28m#-#JbMo6U5xAbJB$jKzn62Vd;~jsNBa1JQdE(XNR2}C6XZA^-s2Ae'
    'BLvnHeobm97$prri9G=31E)jF_MILY+=3z`2GB^xBTF1WeaZSLjw_-|hBZ-&C9ak?HY?9oo;gEIi_nzAg+3P^8>^@vzW4z603(bsWYF_Rc@aYc+QT}EcRDsj'
    'anztk(`kDQv?D-Zh~+TshH~(rhAp;vq6a!jbB!#&YE+|$hF5^-fDov1Jn~N^6p<B7z3Dk<o6t_ntU>SeCK?e#2^CxB6B(d~dVeeuIg-4CTgPNbv5@6WLmnm('
    'VnM8q@Ie}7!GPUoIEvxxl6^=+N9j8-j91LAo`(uxc+qCql7%qSlb(M#df10eB#m!4*90hNr_?Mre&xX!4xeLGA;~tu(L>S!Xq#Q`H4~c8MGg|hDgrf$hm(B`'
    'SWr@%+rYG<gYn9SDjRitYJ_Z`a)5Xs*~++VaEqb@Jl)*|c9QRMTmhR>(iRSsnAse6Q_;z>M2_YTPL!V0k-rC^5jn$4r^)4|{l%Z-L=<a>NYjCYLuSkKP~zbf'
    'kxysdIP{Em&vq{`bWNg*!gGj`vJqmYSk6s$8N_@kq7phy<7O?sM&{2KHQQhKWy!my{Iqk#&PoR-dv8;?-lP<bYUpW<?Ttsi+i{GQVrhPUrMS8dla#hKTX>Y*'
    '7E$BUGh&ZNUcN(d5dn^Nf0E5+M;xB?l&L`xjcnru1}bIVOYDMa-iN1-l4=~evY=)Vo<U9UR0Ks;NgSJ~(W}7`RWKH`C@_tfie^Z#q?uH-9QH}GgYj7?J<MnG'
    'eB7swa^~*yPy~NiSDt1CAPb6O9fwvpI{m^np&4}@^i3fueM~@Z8Mk61((l^?5L@V>2GbljoG&SJ4cMx6OxxDbR2lXvQ!A<FqLBHQ&ajISrYhKh)~jyU$5k{i'
    'S%REb61L7I6b;P0#8pGfniLn2l}vR=u4Yr5A7K@3ge=W-OsSM9GAOE*h#pz@t^m3?kRsKr2NJar(Rn3V>P&!!QaH8K9lZcA9RGi4)#yiD$xaD)CBcT$8!u0@'
    'H!Lf#D-z?NsbFA6U{Coa$Iz+|BFtIaLu#>?1`!P@C^^oQfM^Oxn){DGZ5nZxOGw9v^c=|M4RbmH0uD}c5SkCB39+1JMFD8huf*N93o$gos78Xv>2z(>bw;ur'
    'yTHPmTy+t-SLg3|f;|lJdZPA2f|KxC7`zsl9+i>|GXjrKMmD)-;Kxd`QiFY?&{k05-i@9PAfY*NL@>n-cTelWLQZYt{?p!J{>e%00z-a<iV<iUar0g8LwanA'
    'I95QRrZgeShJ8WYp4TCSRq0^Ph_WF+qM(mHe?+m(RFHQGTek^~5T+7vijl6CH^E5iC`9x_^ehB7ljudDc2nBpB~ax#02PW?AJBK@5=QodM|!jvQz$jSp8@~i'
    'yXy(QyPn{)!WLgq`*+D6j;M%W4opE-EwyuebVhCxs4<VFLdXlEhm5Yo!3pN5IwSi4r_%kC^v^jq)`=u^H9V78Gz#PH|1XSTw`tEZnJ+*CX)0$^irku}#-wO4'
    '^etkDB`P&_&23KJ_dvG^P-8_gs+MX|+qg4m-LL)Jhd?|JCpK9&C_T5Hi&J<on6+mO=~9Zg#hTI)fxE_zkE*Tm-zRzWA_S6-L9q#}faDTHr_OjeV-5d{PbCE~'
    '`2=?iYH;*S`6%PZzCqs)j(x+AsE~|TO^U+OkI|u_piP2+4VsKs+0Z!y3V8k~S|W8LOp}w%)}*Os6WcXnr|XiJ4pELK6n0Gk#vkTgV8bQY3V*{+P|2k-NC9k&'
    'O(wML@sI<)(d?<O8I~9LnxBMtKraNn6v{ox2qDI0xPDm)cIl?UcZ^n=k4BOJ|K4fgCfT0Tg@G8lr)Q(co;B$2S^6CDtXX3FE)cW)8|_I1qpt_tPRBzB0#G5_'
    '#)Hxw!by5%LwRag9wAA<-c^2EwuD8x8uY}8;YD7;%eh!$k?tdcDKUBNB$TK|wOo%Av@tdP5B9U~0IktFhECqNgRBmX2fPvVD0pWk<U2rv+qtSI%#8*$k@zJ!'
    '1~VEg8f$__UBMMU9}J9qI})M|9po8?Pm&PaPSUhgttNgn&HJ%PN}5EhmK~1!QIDz6-r-AKn*)tNeuQ9>Hk9SUf+|tj7k56xV!>?+nVID6)`CK=?B02n4&~)A'
    '-IhcY6Bv^70zQZ|GVqF43Mdth8UgGujU;Z+L*qhw8(|W$Yg2@Se5yph<L8n3PRS`F0Py_SL>8c=mf-?)zHAcogwe@r$<Y9LAPueC@idG@=|kgEVhI#gDDq4$'
    '(bto*k+oZXmXkAKzb5dP^mFmHDBc!v0T3|eDXU!edSXVzFVmcIOL9@!Nmi2^LDb7&=s_{yHRdIukMZ#G)&QQ0rPrE(s`j1dqbrY6_)ya3)|ju;8}!D$NYnw6'
    'W(dMdgno)}&Ndz`vjd6dkGmka0s)0bq-i5W`csg%Xkj3+N_;9;j7B*UDiP?2<aNMek-5d-=Rpe<5r5e%o9k4#&MGGoSpKH7Z}1x<08Dcp1JLCsHG^gJi6Er5'
    '0p&YRUj%)MQfFZA-;fs!U8dY0DI=p!z`!vnYMGIQdb%f9OkuIcHl#01(~-&B!M*)wJ`Y`$RzBH3@N6JoxFn=V`e-Vtk~*`(_mtqKQcWhATf7c7g{1WrT?B~*'
    'Rj3zf0$HF-n}S@L$Px1IjWHlOy_NjE&;wXrtLL8D(leS)k8E2Qdyy`tTBwR(5p0vlCTDNJx$2BSPDY~zPP|B5T6F!QQv*2_)fUtPKxT5Z#DfngPY<PM7hF!u'
    'F_u#iR#{G%%SKos*{7gRA4HCY%8k?%WJHb}tu~*TH6t)F`X1kgT$;pOB2=2nX%+bV2~^1e`<ddU*!xb5{NSJqI>u`;TI8e;AjzXFv_Zz(X>#9y&(tr<6V=hv'
    'yQuE+p={1glXU(z1tUCT!APks10jd8M_IP-l|w`cTa2`#*>ac01)Mffj<ve#Lj#tEQV@GLXN7f{StIda@O}J}bc_kd8he~T{wah=at8eYO%mym1T&2^QL<>q'
    '369eU5j2|SopgC>i*-*^Pf&LeyNdx7`9>;S*Ap|Hw-oFROD(T?!PHY2N60)$rEH?$$SLRv;xguFX<<s}7DnYfH(GVP?}>ham4LdOsfT?IU7L3h>$HU^mPE6`'
    '78<XQeDO>~ATyc)ezbil5UQ7#8?oR}Zb@~sE;{O)L9;+@j<t-qemERQhriHB5ca+U;<z)toER&DC<3Cm8vH1yF=7mLSv@BJkuIE7fN~Nhybtw`OP4TmT$Cs^'
    'qMh|e0a>vxviYcWhId_2CIcVUCEfv!Z}w<IMPa81JSj>Gq2XlX8NpC#QlMNO_zBxuvf=AV0%8P8Od2j3cc78tiG^`Zd%%QA%hM>D(?ao4dS;^#MGQW-7{LYu'
    'ih+dEFDx$5<3DW?Gt80kRM||7NEYE#sB0%>bcENWwnI@f$z3S4cEx4P0C`O@%PGgT7<>xaz!5dgsPZ3^2?LY~15UV0&enm(d%{oxA`UnrpSP5xA%V$~K#Z_b'
    'PJU{fIvCM~_XLV#IhaVaPi}95H8%y8Bo!A8I|3L^y&SUml$nUSKvTxQgrk<EDF<wa$+sz1Z<Z}b5jTYL)LLH5(Frfdw~Dy{ub?e!QL`_%Mi`2N8CdXcC^}In'
    '^DwUmk&5b&O~=73l3<0nzJZ>5o9qK+RJNScF_K6>tCv*~F}+^PZlBZb78!1ky{{s|3Xe<KKE?`{;h8sVH2)-SE|Om{=qm+|33CDOSqrBcm=f=VQc=Y?A(O>v'
    'OJ#WDB5z0quK0i;SUP!$#<x2BMNuO}W#B9a<HPU_rA}&<CUK>>8VT$T4X$u(l$Mrh-0`9h>}I4?*ia)@kQGDK_*2BJi?NG5R2FVBp<vk1k$wj&B?d2vn^nvm'
    'I^aTBi7gwkA1Ck-_n0PZ<Al|C-p&c$$$X5O6{kDYH2YJ8HUhSeIDr_6G)mwb&CeVsM^jo!2vGeHK1NwcIT|%Y&d@#K=Zr8jWTQ5g^mk~E;gDxC5-=87n6DgX'
    '5com_dqjgqE@0>{$*B-=--g0c^jNQi#o~%?lZmD4h-`;NRs&Xgn#$hRTxv+pm`^Q<N6V?&txnlZD?0P0>9-)Z&XYfnK(py31gIq^gA8B9m>kz5NFglADOiOZ'
    'O;gG#H0y37a<)kzkX|=(^~5yLx+gFk<2Aj0a8ZPYqza3~ixkkubPp1dKFaEv-6n(49!#eMZ{2+qb8wd19I==z6A69_4mx|zSxG7Is8rh<Y7#{?nIKZ4>`yf}'
    'b-{$p7i^?yu%a7jiDy}O^`k&I>H5{(zS8B(kIKbc7C)tbnfE*#j{opSx>GvQ70qj`1`(HWHssTBl`taFg-P?0J#CT{DL(QP6338z0NV=1{ow?>A7sbplR}J&'
    'J~8Qp{_WiZU?c^+L<a7jFscNsf=DWV^w8ibUEJaBG3^`5u2H%I>JgZmX6OL6WY54!dk>zxV&%dMcb276uu|zu6#9~IQYE`U8D5&#Rq7o{aG_nUoLpC^D#;Q?'
    '0Zvo3LRhfUp$AuB<_O%=M@=C)ya@AlG+Ea!8)3&MtN6T+)f65KETwmj0u}s`dtuXMym(xKsZ9kH?bCQv(@w&feg5e}pRmYFce-p6HK;!Y9RVv-2r}UjqQ-6;'
    'Rz!_V-p;<Aot36m)TZit(@eTkP+-~WikMj1PyEW*b($O_!RK`v!3X^X`f4eAjU&$LXam~B_L}yn32O5QCQ&mu$5W8;BOJX-QD`!nW*!*~1eLE6p-}XkNYp@<'
    'SCbDBWy4k|h3|oRihDf8LZP5<Gtps_d*@8_q!4o06r)8F_#U|NlbOMqD`BKBxyeUHjT>j^<yA1I07zL^wM;!BOEVJkNPSHURmkgsCy6EQv8#d|J7fY}jWF&*'
    'w)ybgz32(Ncs$G>14*=CQUfp4>Oga$$umIqCy2qPV4gm?6oQvPH+q>A?ITH{{2$?9pWt=K=$1|uTp>aTktP?WIbHgJSYA?YTrG|bqj7^<U$`JHt(Pd$rj*oJ'
    'A0}el%_E<qQt5~1!lD+)BVyKm+d(C%8}x~s^u*jk;^IvhEUzSG5Z;3<^pImIiPo?PT@S>C@G6>4%?Y*lU(OdB4;7g7McMJtTni`*sD@o&3BuLqd41c~wOZw|'
    '6%g;tWPuxWUjzxprwEBod5%pMlP|)>6f`MXA`oL?ZiJMKTnp8b#7wM`B>VA!{df;qLbP==A6Yg-9buU+<3Q8gCMsGEH)Hh*vKMKk<#O9p1Qye<$*XNSGA#oq'
    'mfu_{mf-&@KnKATG>LE~#yJ)(?1T_uH2&igAgwS7xj^iNoS!hi@9yNmJMtB0wM8dqymKa$V=QOXCId%22C2t##vTSxaT+qbEEa&2;{qd1b@4~TEYy%e@>skc'
    'S??*K&GZ#Nd_g2sR<T)5x9d=jUwKj{Evr)ExvJchAZ<OQt&P0i1RVe)PCH>`fRExgB~Zjp^U}W(2Q=IE@YFMWyLV}$RHyvt9p};|S+g!OX=Cb^3x`${c~=`I'
    '1{8P)&iZIzQ|eh(359l1qY+IxV>UUjkzzL^@S`XD<W21eUHB4}hbBQ27na2X-J`3Mel)S6c9dGZa5{sjM+8!R%b_ed$nw1J&IieKA0967il({LaITO^I{lEH'
    'jGT?E<#@&<pg_|8s$qp<EvIi`su4{*4Zu{?jK#QZsIU6^MSaB9Uo%moj*_2;Fepwven`dCm7XCe`dOr(Ea`s6DTF2#GT?oO97Swr(k?S_Z{B)fb5T4KovA9-'
    '#`JU-(Gy8QHj2oI5{i5`W<2pmB+v?bK*d5Kv@V)fTIgJk@7cypBDy@NA?`BD8F`7K2%mM$wCIw^;T3fWQR1~o$#X&`3}O;UfQ^()J7S>HPpVAuZT~T^gU(99'
    ';%z0jbXHfAS%8!2gv90I@-VlS3`-r~^2PZrA$qm<#d0H@C_`pe&4yN*#3k!ayKp!~UduyWW!?BlIH08m)da`V6U||9RJ@U9XQw6LAhSEH45?dvSx*ov?}Xe^'
    'LRG*|qVv(u;WOQIj}nh}L}3YUX(%XN+wEZ%T|rHaNu*aSjjDW>hTG!9H2fU7+FBmDXT3tk3P{c6544JH8<R_+%|(~25{dIlouFjBoG%khQ=zmNvYS!mL(5U}'
    '2kAyAsR8PKA{&`DDuLw~q-tV!;)ck>upxNRjGv_m^*b0x4SHaFB~<?#x>^K2(}l4o!!-#bl!-E_giy2NnLrY>GT`rcZjcMtrz;tg6*=@gh}jS`Y{7UyOd3e$'
    'xF#IwtZ-t)i!t!P5|>be`!g{*RUjFeN%hcx#M82e%LwmsLy#_3OiErX5LmW?g_*T+BS-ci2vraQs)O!OGPh!&eY@+7)D%xb^?%AiDh*~J+y$jH!;nTHlHn&o'
    'd_UM42sQj~Wf*bwl(q~#?l6n7Vw{Zvs)dIpl+`km)AFyI|NYNnqw@JEUtC(`jBFg3ig({`ona=!SE#ic)f?RX!5nEQ1}QuF&V@S~x~{R?8{c%iO9K<O&m%ZY'
    'lrER6j&WI9QJL0!wfJ@T>Q+f`|IF@qSK>OXkqQ}_$6WEpm1eDSe1HSi+}f=i)-168`lJ8;2k&bXk3k9S+KF|07kYPG`M6j8AYOks+CARdsWd_2)ZkTMM^mEr'
    'Ou3L#(wBZnpA@Z+{JBMDKRq+%cuE&15r22k&gVx8a|;Z0csE}FBoKK#6vaatWCu&hQTE^eh)W|y^c2uE;|sq%ER#P-q8X@{Yl-YI2K-E=!iVyT*vQiJ4D-@;'
    'uB;{}Boq0_2ye<omMM!&WYWQtDNED@J7>zbf|=<Pr60=`a?QPiqy2dxobS8-e7k#Ua%)O!sn^Mh;9cy<HLGYgB3kp5%$z;2^c&P-(4j@RGFgGb6X@ndis8V>'
    'qzcN)G#lJL&m9<ZRwXlKU6JG^MSF)zr0QqAamO&o0cVAK*i?f+eUZ))M8ectu1jzYqyVNw%j8I5C!m1|Q!pE;woa_*W}%VXM*M(&InQ*_4(DU6Xu+KIFj|zs'
    'g!C+ARZU#fGf|NTU5T-=;%_lILIIsJ(Y>IiV~;FUmf%xeGGN187nBXtSq=bd#gg<~g*$`5L??uHMP)gY8}d9B%3vycn#>vVk+o7RMn01njh{*aMU5sHt|jN<'
    'p@&XcXuLz$Lp@h_D3cf+Ub5~8M&tyYoKBx59_Gcn@Sq|}Q93X+uMpOd!16GOGv+iLn7S6OeDk#Y37VMe{6*4+OQ=OMLOD|hHs5jW)4u1A+_rDso|oC1axOgW'
    'R81=(W`tt?NJF@2u1od8syEhI<$@=!*OeLel+P8fu~;dt>AhCK>!d>iyWyX8?RCeVh_}z5mlpLeXWn=yK0Pfh1~3_qz~I!84wH`4*_&oiSBMZ%%%;Q%qCv^p'
    'L1CeASiokhTAwsH@g+dRpM`LPk;rKuq&N<}l+(U0C2~W<gzWh+23+3KEMW;ESJ$g*zA%v#_mQ=RljatM2cIJi(%IfUvhWB|DA6oB=R6Rxk1UpXDvK>ZqWra^'
    '$pCaLzAf7q(c>dZYzyx;iiJY76*JP8#QCAQ2IJfvIHJml6^COOoRHuXnoFh;8}Xbp-orzWhc%@xN@n>ZLG0uf<xG)$DH4H)P-33IF{Zl`fVtDyMU_aLN}-~b'
    '26#P*%ea908CoV()GkjdDf&q-%W6i4Ak~=FOL4;rL&Df~eR9Htal@76+y}{~trx*pwQevNu|-p%KS=MG5KYi3(~&i$m;>$F8^f9uQ!Eo!AD;Jg+f!E7)Dwkq'
    '1`Q~*Vad;CIikjb0y7}6IU*Osj<+sG5rGLzLFKceu;M6^>w%7YNV_Xgd|B-RdAwmUl3@u(ZXw3{5f#W6%LHXSAR(sgS@vGBO=@8_Z=kGC_aR;K%}Ti2mC=|y'
    '%nX6G6`qU{w-3z8)X~e4ZKO<dWO~FGy4IjiaY?6<Lv|yRBycnjjw}uem)L+yuA*$UNZAI_X+3P4)Rm#pn6ruxXkVItsZEEq*3cRkS-TlYu{iP6ZgT1_oq%Ra'
    'GY??n6zTnUCZ=jOLcOrz1~f#u!QAx7O6LkQ%6^*dtSzYNGA0QZVG_m%GQ@9F2M}k5qLMZjV$PO-aW*9OR3Z^mT|zQBth|K9wNhU~uTvEmAx=?SFO~lRqeKTK'
    'V)+MygQOPPb&?G;wGkN~pzZ#v=zt(NK#K>EEd|;DC0Hkih`g{i7?o%rqW*_4hy4R$MHY6U@hVGmZ1=3c1C|eFK<!7C3O6Y<{;-4VfsG1~lC%h30`+MUI$Ah&'
    'im09^oGnyG3zJV4rgtOi2x?fky?Ae_Tp%3u_qoD+!3=Agk)=p2<mCif1<O#fgtz$jdPI<ml>%#~cT}|;<-~usiZl9A8TCgZpFx<h*`bT}DPnz!NRRU4fB!@J'
    '@B9et{0j#-(+XF{63XpbHf-qR^@?%q*zA(OEMZRgyh9qIH^g8Uu|;KfY>EaPc?Q_F<Xa_=j_{KnSE~o<K2rKBy`GX%l;f7Ynw^d#5>bS`n0J4!(o5?$jMTlt'
    'A;A)$p=^3xy>8sX2J`-rRaz)Vd{^p-f8gcRQE2MBbn30NCUP*tQazbkejy9P9XQ$n;q}eX1z^&1>2siKEDRz5*LR$bfJT)lADSvRCtAy|t%avO)!MKMX?<t^'
    'Z-;!}p=)R&={0rZzZ}z1JhBJSh_|E>k1yDY-?SFWqM17S1Xx7$#Ss+YVw?*|M3%l8lMP`FRG7c(#FkbejJ$M=ir`Qc3$Mp%jLMXWH0tqmM>w$2F8&-%EDXJ1'
    'a^@J<U>G!aYhLf0cxT3q2mpwKB9j^<x>LB{f#L&%EEdXiC?d%O(mcEJ=$`IFh8Dp<<__d7_{F4~!^c?j0oz2H!}S@fl{Iluk4Os=d7<yR?0~QI^KZ*p9dNRc'
    '6^`kckPT|Ggxv#kb2#vZwBa-!_#^1+g@Jdnx-D@fFJ^k@C~;Uofl10Fnepynb=&Y<a3e?TqTwvxPz>Nph0=1qum=C5JvF%zCPeyR-0Hb)Z6oZ<*dL!e#v6NL'
    '`)6*(HzsHHWVQGl{p)%1K@aoP`sD&`s_`qKbI%X>QWfD`n*ZTrR{$L+e1}bIGQwzUR1Nyh74EH#M`y6YcN9c_p1125uQq(bL}R=l0a9v7I;Q5?Wo!5FQppR-'
    'uqV=hB0S+aqEO7ynLP^8nS<wim1INf$-GgO_zvtz&$9{I{@!-w@T4+7x+Zc3`-v(Z*vM`T>^30355v~?9iudlx5{3R%ypRj^1dnbxFEc~jhmS$Stw_!af)|H'
    'l5etucd+;l-l{rsjKgXTS~jk1pYD0?!O+qrHNes$mK33JI;AsrK$#|iLn#~|vn~g0#@9;c!7{QrPpdC(x}oF|9cNy$$-YM%#gXjg02QPd(C0bdR!w70%l~lQ'
    'kXM#aQcKLOAa?l>9Q4tZd$jP+jnhYdE<8V3S>-E?B*$`29n8ZZ9Wi+22yqbdKJPCgL~XkVFO&gUI+}8l>Nzn8hjY`Sp+z2$8sk&XDZZVyLa=A9&wC?sY&FFB'
    'hHS5Eyt7YFdrk(Ur$<AZwmf~jOM=|Fa=vxFUeCKi-c+-Ifbi_bcK8l3+?jTUEkKLI3Uy{ZbA3weK_X;?HM$NkD+a}a;#E8IE^OR=#Y}b`$8SSDhZ^CT#vdf}'
    '@HQ-73JxTtX##Wx!Bs}C6QIOB<iIw3>P=iv&X@M`HND1}GYmK;kN*YJM(-ef!ZJuL7%7mrAg9X4K3<uAfTzjd*f5X$k#Q8T%+@rC7)Uchw&u6b-2OS}m99@4'
    '%q&xIfJT8N5%P}g2qDf?w<!A3Ct6@BiVXzw&h@c*CPE<GxUzw>Xx=!X!;|G`-_{o9SDzZ6+&;oQ#;J3}&7aWrAImNp9H-@Z=Q!}x)&d?;9lC?jM}D!_F%}kA'
    '))tnFs|&OaoQ*~Uzx@39)z#JfIdR{7+q-z)2CjWRB65r*HJ+dAIOW$C@~e4Z!#vL9JX0gDQ{zRXWlOcJLMXTo3TwB6TZ%AqeIy@DN|t&sBw;z2GXzi+h{Q61'
    'd{y)ovc))gvz0F`EmLn>t1EVC#px^;7wv_Gh0<EfSzYQDTg%HOXQ|lkE*4f+?Lu*_>o{u*D|WZ-wBWyPsk>C{t}c~Il2NwB`AwKBv<`^Wt#myV&IC+#CfSW*'
    'Hc`0y7+r^yd5#<ay#pG7b&c?@fc23<ybevL5vGF$Nr<7-G;_rA2P{L(LqFFIn@Z&=q(rD}O{qG-$T~f++eyrmva&8_@_=O88Pvq|u%zOWbS5c|YZFQqLP(fm'
    'O7M8WB1SWy>u@eYA*@JtQrF-oG9cdXg<Ot0jL~w=>`NEL(2(Yvlu@)g`-&HM$tJ--2W4?N!5rLvWO=7OwINHn)&v3K)Kr|L2EZFCkrEciYVqtitoyjQX-0+e'
    'B2J9t#1NDfzT*unL^_59>Ii}hL^Q2KN_6uq0@L==9eVu>y56cdzfhWA2~TQRR!=Dxj9~K)<A`_vP2+ZBn>3iRXpor#3MVwnOJ!dY0u-SmR$$6%+Ml|kvvG^2'
    'Ji~jQ0_Q|<IEdG>XsfB0c@97Pu!IQz0-9@ZLX)z+YA-FWuB<uTLaDvt*vpHp)fP<8&a%C>vfM4eo2B;R+TvPqajjD*b{Cfyx}}9yyX`p3OAC%<&tO2bi}|!c'
    'Q%q$?dFd21CovrB2u;6Y-sns~v4ZtiQMx<s^*90oW;IHE2^Xfth!+Xee>^;$sF-g{DOYrIQ>~d{NntCs2SYgWeLzSuV;fd|M@?=%?<vl83(Y8(podUF8PW^N'
    'iXm?h%;PTA7&Tl3*Cp>BFI+I12ouk2qAG+r!0^B&s!bPz9<JitxISxm#Rp)4l7d8<!pFF@s+AvRx26me4A4h4wG(6YVv93K05Jy;)&(oFlHNNg&FB;<9W{kX'
    'cHxd}rZPi<sVc-aDL*94r4S;$mL(!|mI)rHy#ZJf#3;dR%_MOKt`AZs-vh<7he_1jE+sD#Q1^CxIf8D#<6gQQynaBa(n8bVg>ZxmAxUBi^pWZo-N`vp%O|P+'
    'Lhd~W={XpWjIl5EDI_Es2BdWf%nWq>qRR~=vIBzIk*S~s{SE~*(F2xGxGHo!N5(F2zz@`cdF0StvasqBRu`^Mg-Mk4CW6C~OocOCp@nfq8l&u^4;`SzPpyKy'
    'EU@-z3wV^h*X3f!%@mzP!M~)Zxx-*cg2|)S4MY(@V2*jkG)Iz+iJ)c4A8sFL8YsfVuV{DX*^;nZzz%X*>wCis8?)Dv2lGSib$<2v{%bPYc;IXi)QBPoW0IvH'
    '2xgi-ppr84tl}AOPpXHUSd*u=)J0kE)YsU+(wJvY!RtUjYUg>9lZ;q5E*u*z{f@HBdJ}m++<<N=Mezfw0F}{X3=*#Sv9#LUt{zvC+_53gq86D_&s;(+!l5bM'
    'AL#%3XJHj`CrD!S(0!~#56z#Tp0pno1YpWIP8EGwkH%cy>*QfK`Vt-(x%Ax$$fA#>Qt_2ROB<+LAkIb}&0&AUR=V_}C&V}>=*w-z>6-1xst7tI>|y(?wD_Eh'
    't_!K2XVv>)>vOYuyi++ov5GK)ps)G9p>6;shqN3mikGC5+|6dzcY0mi8#T)?=kYA>y!wP8l<|1UR6jL>RhjG=uE+!@FXn((6j{r!na!qzv#R~qKL~*R?|(3('
    'ck^KHuz7S0OPRG&;Gz3iDz24z(&JFk-M_K%V#xq2Asy`RXs2;RmH?h;#kJ<q)^X*qhWRJrvyBR<4AUYy9^*J)joluOrOG;k1_KG5ZqGgyRtre57ViS8#*hOm'
    'CzLZwzB;ZPRgba#+YAN~yM(^a8C^1G?hp^5)3sFc9nCwK2rA(Ly^n9fb7dbEzfqTi)TugUPEUu)cSfawyt2^?7pbh$i$_14vC|;@Ist0Xx~w5Kln4smWqdCP'
    'W`HJok)l|%#+_4Vqy^j4+a6wN6?B%u>qP+aB@Rp1ZDATlu``8t=~zZFXB2}d)X?3$Wm%>Ll47nE4vLP##=J6@4(6rL@?#FS?vw}y^Ayh*hvo{e)^#pk7xBi8'
    'a8w;utOKCg(qb96C9?25S2W=##m6?HX#4~%iChDG+Js?CEKt^3Brjx4Mo4%x)W*EJdYSKB5LYS}DTob&I{DkU&v&6>qn#m9oeSP(4nJjbnZpYFbMh&37hioS'
    '&xdM`!HF<MW5Xzx3I%G5(2GZd)HAi}!B(wGg~Jl%zNT<fjhxTf%+cOoe{D5S-c*kO&DUGU2OyoB2V2MQDzyyn+)+WoVdP!)v0c?=^v?U7d2vCwjz>oJUx#j4'
    '2B*tK$i=1n!mKL}Iz)~+OofAK+UZ=?LvW*e#!8FkeU!v#+7OS_Cyn|w<r&QESGV6)b~1dS2erABTjpM02QzFbS1g$Kw!<tc1BL2*Be2M`B>5m$FcrJ#Mb9w$'
    'AX@Sv9n<dy$<e(aY}Ya@^mb%S%aTB;W8&755J|L~*uAUi4YNI{Ep}r}SL~x^3CkfRDe9m$99&M`p`A=)>(X-pGy9xe-IwUcWq8mJG5_UKiqY1j4ucj0GRV>I'
    'g7Nr}(0Lzt2zNEqP4@GFbR;R}_7laJ+Mq6nH)w5A-BF4yE|kh3vl{U|WeN+|_my9L_|n|pIusnl8`QDAX{CW^REz*^TUMPfJ^@BoGDGDIstce(2Q?dW;svXq'
    'X^m*NqeaDU>=rE1+3VcIg4gS#>)dE!@i)bA*EnZJ*RrKL-8`1zFB^F27#(z?`^GYXjGj=fNl=UK8_V#g4ZLcMtI;iEkyvexFbks&);?b%T@DqcMJKzMTQqYp'
    'Ve#L^+!8%6nPx7OcRsjIjPlQ$bHPnwc}zubn$b4Js?KYb^o^2pJi2u0!Qep<I4p+2c@Ivm7(V22--@>`q=gk09dZiob=Ao^bO(W5K0&j%?<;T9xW}R&jliBm'
    'w@GuTur`(FCAfW?c0a`I^I<Aub@T+V$BdO<Xr#0}KVMoi#LYX{(iO~i?`l4Nrb$R7(lUd1ZGiE}Dy}Alf`rc(sq0Zub3vH~f0Am+;E^<C2X!5FIPvpQX|cdb'
    '7zinH5BtW&*ascnc1KE=7UC%)($v8!kakiE(IH3loro%+2h+Cm$iTBbiy+#T=Y@L{eQoe*bmcuCoedo&U&%);nmPrc1sJt$yeY%&^$b#ip9@u0_(evzA?kpZ'
    'jrQS%+v(FCn~FC$*Oo4_fvyvutP~I~h}Xh89>W9+ayZd?5_LNuJhXT~c}4Y};sLXAowvj5ych>FQEa~1JFZL@nPyI8YOwM}Wf<BWI+wK^VT~wHEo^8=Za{I8'
    'FAKp!P4jP4!b{>Jl{v>!Q9@K{u2^n_*58zF*_^UgCRCcbIK&p)5Ib|UBlg6nK&zJL^|GEhjhc}|mC8H9X#{B0P;ZVeApz=g^b!<pE)POeM-4^1Y#@oA!6i@@'
    'bs%co3Q<5B7+4IY74BejxU$w1)|GaT6wHm$86_Ggfh^*#)U>YReXux9Xm$a2mvQ=CfXxLuDtpQ<K>zTKIb+ReIioA|n35udSwsq4H<;a9IENj1$umwdoG~RJ'
    'iH$%2G(7pEQZWch5Xm-#X(_F6ioipAQkc$GkuGTx-7c=>N`+jhm@AcXrG;E+NsKY^-G)_SF3v7sozn6K%0GC!%CAeNoSiLiXf=mR3r%`#qULi-TRIx4ase&1'
    '5ytZRd7p9!SNdGfNUOggk4KODBTFwhhihK|UyiJ0l~#CjQZ}QVte~A9b;xq+qEXh*Ge9lAXD86Z8ae)PQUSGIsZyZ7OQTU^BbiGG=(SRiX9Mti^XF)ylS|Bo'
    'oV*SWEy19NGysLbMpR$Qgkcc*hIom%KQw35-C>zr0#Xf~Hlmj_(Hl|wpL17-ZQ_^=n8UXO%iIind`VN4_G*A_#^`3Gz!-9?gDo>}9E;1B7jgx0!cjP^1N~h1'
    'v4<3f!SF6b?$32vN`>LyW^G<`QLF1$iX{Rsazu()9=xnsg!z+8g@mE*EeWDknJhwDAw&=%bmTUd@Gd0A=9re|Ll}|Kn6nm_3W<X+zbB0CY&O+jpm9ZGZpjQx'
    '8p@K8B;L!hn0mg|J|4%3OCQ~2uS^%ojS5*(T;*-|vstCbCZNj2iVff`u#WX}yYY7T7RR(^ZZq4}Pnq&!p^(d*ys1=<GUX+F-mO+oDw*;^p>P+pHoYO5_NmQ$'
    'dQ;hg&K3do_SW%n6`n!lN+AJ_Li@GjtxvBi$H!l=9K1NF>{kyn<<&S2QGd{eXcq7-=vxn(qqQFM2PTDyssrD3b*jE$-LfrF#(#6-hDmaOXUcNnoh#-t#K4#l'
    '0#mbRbiten$@83cFJq=0Jm)ebpfhFqb2nvm(8FJ0x!K=(RXtYS<i$t%LPhv(N->^~Ho6DIA&m60IA`ZDyC~}M!A^}JSJ+5s;2J5;QH2H}?AQh<M6N$ueMF1F'
    'M|mJJ)ROL053m&)bxQcS_!>;QIg12$$l4W!VrD&!E}N;sJQWG<hF(wEsJI?SO;oZ>lZ{t8i=g&^aFa*qrk-!{Js08JB_d6?xegYGB~KHG{T#Vxqumg0A!_xE'
    '_!Zc+TXZx<q)_d+T^Z4+ZKnudP#<?=+bR+5C1`$K(9+mOl8T%<3@t{El4>BmgyT)eOgk(rmNWjLGCGJ8#F3984-0;;%bQk10y@eZ$vY1);K9iQnJ7~83!3?$'
    'Nmh=-Cl8UHTnA(3eNA%~1`;xOPzYnhBFv307AxXy3BIE5$cng;uvqwz3x1ON1wIEKJC2Vxc~}7o32P+kY_c<Tx*!<Is!J_ayq3bPDst)SRl(e}M5ASfC;H5D'
    'HnOAyXbs%<`B-iLBph-@(;qYV`jjnY=nNc++ov-J<Uo+dAEm(I*g_28!vSdF{c+Mt57J!5uv_PMN!RE?i4co~`y5@9!)HTM36z9Tj1Uqv>C!ve+kW@qD5BL0'
    'h>b{2kJJ$Wjm!(BT49mEepwO@8gl5U<hSc+y0M%gBaYqs+WCB%B3ASkZOvIOFDs7u%R{UseA85e5tH|8vOvN6H07pV)OVazgznxH-q-as$sh}dViFJ;MVchg'
    'YL?%JGj2qtA<N&UV5#q7h7lBk(28X?NuSMeXS<HO8<P}xb_bqlq0i-u<_7LJmP8m<vJ5CB98s5;YMOT@s$-J*T3n3~H34ClW7kx&j0f%rZ5GM_8qrOFa4Uq*'
    'LpYg8jGX+5G~xjM&fadUgNYp?JFv%&;K04hhZU3?nBt5lplf)V$K}lFv&T3JkYg0-D2^k}b754KbY^NnkQ#hi|L0@GM)yZ)Ef^EkbHW1;evy4=YF+=dRYS8X'
    'fui@WnE#(KU@%4s1MT|t822cpBQ)#8_c97tb(=5G>6}bnth{F&S0*I;nN3OfydkD~_Au~L1e?f%Tk4AOK@W5#%I7BzPKhB)QYF@9Elb;p!LQNH7<yNXBvshN'
    '%r1G=aERd3Hcyi@7Tjs9b1G`hTa>1E1%@9|QfnbhOFEW`CG=gV%W_uh>?NjzjdYgY;l15ru@gDCFX@JK^S<r~5se)ZXeeZpsPlJe5=1nZVMloAi17X3IhSI{'
    'q>+JjflU*S9W?Ggz^%nq-5W7DJ#!OpzD>#96x!C)Q~l}jRz!NPVum-i)LJ33%58*96UHKHaay<9SK$mm2~^I5@vkiX+q;}*-_TE8KPY2pjG5yVUi^qjCS{P7'
    '>se5?%!kBCH149d4%48{{TEppLMFS`S1lhDZ=PAn*?$DENa8BowHGi!V4k|HA14GGDUJ{uw`q32f<i2d>&^6iN|D#^5$#OI90kfDu`XUHPr7w`w;s1i)#-P+'
    'GaS!T6QYCg6fuP<f01$?=}C;xvgOxdzhT1uP7&j4MB#eK<J6c_ui4+k3TNh|k_jS9l7g-x>mMf_z@*y29mWyBNoj?`J3;3(MFEIq1(kKbS0gbGRSZa3x+BC`'
    'MEnu41v#ZL&=mhQNTpOroF#g8sVx4^EhPd6YfD0?*C`SrmtCfRSK!}9uAW_`Uu)vuW%zd${>3j#^lO>^UBP!UHFdn9C`Z>*xQ6S42qW#Z95UvUhC~F0kX4oo'
    '<dJyDC8y<zt8nE2o!}+2Y?imCa9cj!ym^<%IRctY&5GVqGsQC+wWO^-qf|N|jTNjq```vFk|{T-g39Qj+uk0XDZXh;g&d<_!-~VxKgT^3%8Apk_&S&n#wq#K'
    'P_3e#gyhgv3gtmvdL(?1aUA`Debo;-ZI)BL%2cwMn(-{;Um{6UNQb3t_XI#`R=(ngIV&mvBhHfqN46GZomyWiN6}y=wHAt<PWBl`7se>pmSdJa$QL~^i;Pnf'
    'swAm(jkzAE>{-1S4>6b0xk6p~#M_=)-fV5#Gik-j<4ajv>FeQJo{$+e4~XiNy8bvGpojG~tq|;#G%3;oh<f7{oteM^CT3!N=|Z<cs=P|OV_%>i$ex07G^Rc$'
    '?A&rRUS4y~>9SWVki_-Mq%6lH>T|5dmm^W~ck_G$7@>~VOFWkg^dQX2_$EGI;%bp3On5s?I^LxvoD2No<>Wkmb^Y$H@Xex{nRFM+qMVZPryXc!C=qk=g<wrf'
    '&)TkMYfp-Fi-t2L?&og=oA}BH!bywECE9-AG&|u~(&X?Ujp0>9MDpPneGf=wwlbqc3+a^-V$ApPAbO@{4^pi~qa~6BZQ}V1;5J!1C5wE*NiGenJP%YVzAE$f'
    'D4*Py$8PZ0qR0t?wRYEOj3$oEG|`*zZR32NkFpTJERrXLD6*NO``8U857LXkBDt+NZ)~Ys5=1P9Ondk^INvD_$0NW{FttyfJC!SF==kli!{Lv3nUJVLX*_`0'
    '_I4?;-pQM-o$4o*XfKv;^1+$(@gjw&p`36~Oy1rX+K7$iqm~|rG&J@0k=$EHNBduzwLSQ_Yl)a?=w;>eQRR5=pmJCfJ_IZ6WR_$u+MCs*(?F#Z=O4obhYkf0'
    'z?@>XmZ_=YCI7uMlycpVb?ZSXYGHtMG6`2(vbSW@DlRUT13ja(Nb?O8NmSbsQiI10>1pRT6Y2A>AJmLYZ?UhQ+!cYHJd>Q3mA+mMBy~ep!Bibqo%A8k3`Da!'
    '->lNtQ4)GS3q!$QxggSwZ`o4m?1I6;V3*CnTbW>FQzb$o6n;vtEdCI)^|V+UnG`=k2WpRpz9;N)ZNnHtHO05sLZJ5LMZ;VSH2ZkgVY%xar1VQlJr^#?#0!Vs'
    'X(35wcniM>kY$)p66`3BxzLM7xDS!9u`Y?%l8GgSeMEs7A<5nJFro5yV@*U4l4DJnjnf6=za_2oW*#c2qH<{l<<iXmR4&c1T$)LiOEWB&X3F&$luI*>+ziR3'
    '8I(&iO#hjO$))DUh2q~hq#tbKg-+>DI~xz}{PSb|oTJxDmf_R*Kz8#%Jn&~7pG!d}&&d95e)tnw{$DR&kF}%y>tZXnZI4DhhtCFeF+C#YI+AG!a>jw@VFbQN'
    '3|TCglwCmHW{q339LeI3K|ORwW6qr@92t~j5YPX)7dD<nAxavU-e`!)Ixr2De*7Ki5tbzUZhPy<T9iLnGql8kb$G$OqZev@hSz=PO5A%FITgm+CA>WncxEtJ'
    'uuRWLKZMt$*&0tWW#rw6Eu6tzwwU{bH&bMBP*Uk4F&rAa6JBh+T)4gSCTFHZ=n+ss6b)Zn25V!dDbHGI*^DvhMxux9bP{06+W1`@-N!u0q>>UA!e$q6v=5QP'
    '>V*hFDbEyUSsChq@a(;4+k@$+-O{eeiXU>L^xQH&FX@2WI@+I>ym4C`lwH?s_uyN|pjQ!!9Fl19HRyqXJ{xi!CGDZqLrl?#Zl9!hd`~Iah8DjU1YBW|Ge_@9'
    '7oALA9&&vN9;HoWRWfj>=C}njAre*dJE|Y+Dl%5yw4i;A!ANFC-K!WNl1~Q{BAgZkME+?>zJ9c{m`sgGke6y2Cm4)9MSCTj=MHHD*@wi)u%MzS862Cq_bXhS'
    'C!suksL-N~Ju@ZVi)2EBH&7dqI&x^l<c@p4I7PpzBs|};nvzJ$C&o+{`y52KVlL=n^op&>&<Bzv7F``3C>5)xx#>c?xYM#^a|wC6sLn;xy~nxPtX?GSIhJVP'
    '7Pk<1bfp*Qx879{E@>st$91pW9uFujI@SqTm1!o^y9GxZ1=960UH2Q@*r+psig>m(u_Ojc`II*hfc9P76shMu7w54<fz_!~U>*6*B4!KE2E;fNlgz0a@DQ&S'
    'LCDM+e3GGp8d;O)$p86di%ci{8=G<@t2Duz8ZZ@2eJ+6Oi#D)66_;}@aY2=ZBG5EyQS2llYsU84aYVp2;dn9pA^o;0l9o@xM7PY9hc@Ua)h=<~i~zJaFIbFj'
    'Fko7^p%u@Y^89%zW=3aaYvSs!$V#$lg}#U8+GfPLnl#$vk;pPepr7#r^UWmjQ#vT={#MhDg&wBcP-j}jj2DEJ$BW{L^`%@wX8=`+uc3L>yRd}GPw924*q$!1'
    '=kA3l^u(AyTMpuMb`xP<g4>d(<#Y@;3o-^zBfXTan}xqGGE@vJECIC-$CVVJAw`RnR}_XD6=G7xM+ZAJ(1~&(y6VZjh+DBBmzfT%o|N%l5s@VW!|u$7j0gF&'
    'cr=2S#l{rIO(AS(7z7j=2(v7S5S2^vvIeCc%NKI{O0IZ?MovDe%`0&!r@lJJF6HDAYD&ka7rh))imt$u>BSBY%0(VC1zA(G2(9xOMJwgxqIPoGx5U}Q;N)T9'
    'E>HkuLdTG#jHHd>pzl7Fjc*<Q$;wDq))H2He9y0AnY#Sm(0qCr5={qS^+;8ecA<-0G|l3EDX3i)-4qtQYC-8tK@$&v#bzcA7p0rR1pV=>PJ7#x=Js)A>p;FZ'
    'IjB}^Z}uwuTV$XTbqQJ!myj(Lm*s7bC3(Ia*occsR*Kt48(_hzWg{lsBTBfoy2Rz6ig=BJi%N}TpnSG1sHzb^*!tDy4oJgd98{<XM-iigoJNH&P*6i5WlrYH'
    '*70HUq*le$5mM2^0&(cb0orXenS;Ikcce#cTG3CRs@46-(IW{(urzTDXby{^mtyq+<l_4g(ax<a6)1GPHzZ?=8)_}w5FHMF!{F!RJW)<?^e1Ql>HySS%2J<b'
    '0^dqgznpA><N~|8ET8UVK>mr->v7n9aHEI1!=k6oIXWHvoCaQI(hqXX&^dm;=Z)s0K|LY0H?%p!*TzR80a(n3A_4T#9(f}eE182Qe9aW!q4W^Z9}Zz4ehb|U'
    'P3a=gKa$jkoaTE`7taSwn-8HFxsi?_Cj_ag!}pAH^3AGhS1srXF;P-)g55gFzln!K0!}P7!t6e$9SKg+3qw@N^BLj<gC-UgF$J==BNn~j$>N8Q^HpA-^yga!'
    '|H75ZDiUA0krVGczAp|xAp~ECDJ~d{d7-0c5|p$1-o1=qt19M(O^()6ZgW#@5GqIce7on^!z`WL3toyVk9D+yZ3N8$f<allWCwy$bDZZid6?$NR&H$N#7>Gb'
    'OYlCWc(JGWu)}_LGrUWuI*-dYZh<s2a};wX#+shv^i!q9U3SeNAp_|&=?XzgOi{v~jcQEB0a1GB<&_}oGi}oBT)3m5>l(Yg@lD6O%=kv_$}_e-7o&JE<<ZHR'
    ';|$~#Q@H2Dn>R9N3tuY|EE~#b6^D~KvM4xrC!&c&B(}V_3om6{SZ<zd?N_3^H~9W=tG4&C(%i3X?O59~)3Of>SQGfL6E1Y};pphNa&i(B1k0*7X=2iNyk3PU'
    '7PJ=M`5D3|k>CxXt6b4Ck8>`#^`4@qauh6x$pWwqEeeSyeQ9-73V=;(d2Ko209mAmf7)OOaoNjkXf9&~iC7Y?5=x7d4r38qF0$o8)sEA`S%KkGbe%Qga(kDa'
    'QfAtnic^+1Ef^zu1t2E=;f)MU3y>?AnFE~px<#RD#T7?cIByAH;m-gdNXlX*fXl0D|NT##9jzz_X@z2}NYr)PFl*1ePBt`z;ei$6QO`^^ZL>^IswyTPU;lwa'
    '<h1d=Cb~Qc;{ka}Qq0~t&UJiG7jtmZMR95>oO`jjRuU!>@^r#(_SB<R@lCu&kSE&ugDla_%eCg&4T!t7=3cFG(0ub(O1Pg)dnJxhF0U;So6ivoF%-?}!Vp4w'
    '$KFnuGAqqD)#JUts)woZge6l;@C5BJd6G!;@Zk2`?3BQEL4ve2DmeCZU!c5<kS?R?v!YJ{r9R(mglhdo3-kp}OM+&R(QyWt%!6?E=R+qlDPG;&<Rm5Sn1iV;'
    'yi4p}0d?m1!!~-^LQ@P2$_y@9m*X(o(xD_0KeofWBPzU^wnxI5Va$8;9VQwb;oSV1(<w!8iLev)3R$;!o$C~{qo^ECtm_CxT@M+Pf#3q9RG``taGQNM;?#lw'
    '9iu&a_RZ;_K$#hn(k17S(l`{`^FFHQGv%p5qPqSdJZP1$WMd>7X&r&~d}kz*a7GstEwWHtYb)=w4X+vUtLQAwhxp~TbRX?TDIuCL*ttux=@M?T6*4bSZP1D5'
    ';PQiG&X?83n_-D9ZcMN18_Cc@Q%WNE%aVu%P8~lsbP2?_1agOUq2%c2H;`tqP|=CkARv?A7IU(_xnk5!-5uj?Efy!)7u6eaPqtO(f>Q;RUL;XaMRHR|cqp<@'
    'MPvvj0Xeo)qB12gZO#c`q43NABF$GF-B8}tghn3bcu0YGuP1^>JmT8ApbVJEAd2gR2SOl|r)fj2$&phb?dg{>Gu#B1fX=KcmxBV#)l73;+mhmU@iRF3M2Qj;'
    'FPBCl{^V0vxu2ZRHfTC>%40N%pvrVjzx6rpV}U-zn@J!5lG9?EY61#t-`<(Y#d)q$C7tYZKO=`mBDMyILpCtk-VLH*V%Jkot;s#n!YN`#;h%a(;^D5$%%oBx'
    'Kj8sIJwIO<JGtg0^v){eVwlT!9JXi`B7Ta9Ie4#sBOK~U*-5lQx-SN_pKRzO_3}J-3H`eyo`Gk>?T5#rp3Ss8d)PT~ZyZb_X6CXP(vFUt;ST0%DPeASiX_{%'
    '!B!Tz#;6=j+yi3VDtVisMh$8blvuoh?0-b(kN9ZfGdukN1z4aD3{;+a7kMHps`%X)Gcf09WpHK`H4`*}bE1PD^Bz6m;`1<M;rZy(73JuJ;Hv=hppZCxDW^yV'
    ')Z>L++~n(A54<6{zWK&!(U4&or#-J__dr`B<9CK$&zRE1B5vDl0|T_&9!4<8h}g2x8@F9}D6Xv=uY1ll^CULrqdQDFT`)&3=#lXM`Dmyur^e}y`|LE)FBF|}'
    'o#?!NfA51X@}!GrpW~gr&hYueF7f>Df7}Zs83^dn8M#+h#Dyw2lv@XMJ(Nt83QsNDci^G4lru7W1$cs)Qot*W@be-)wVa-J)x_SytBn712+OH_%V)mvj-&Zi'
    'cu805siHmaG^1W>B};ekRwif-a9BvjVJVKo8R*MS0usgfLJSFsZw!kS#6qTq4X{`)Bw<l1JRFO{{Nls0SVk=Lq_hDh#Zn?F#XlL8mH43GU6R8DT#Af~$cL-5'
    'Mj{#u322A`k6}?tphp4*3yeW!cUNyerTK-@KN^s!yh(dF`bZ=*MX^+R_(&}O@kr2St3D8g6n<Fx_XmQ=pk+7HiBWj)3<-MpkP%5E2Nb@$6QYc+)@r`quU3!o'
    '$~5uz&EDZ|rMbJccL*<6=L^bPw}Pis2Tm5-$Qjo;qZZP$uAw;T@+dd11E&!d#~ZI^7^j)CT<@;qMf{)eSz8jXjoIX4!x0sfx7mPrp2wHj#CE+?hN_o_msyZ-'
    '#+;E-rC7j9kt)T)lu9&XW;E^Mv9aU8N=lv{x?z_ofR$>vOv=k*ar4OQ=h^Y2T#}mQQNtoNW5Y5EF}JZ!N{Z}+VYoJ)8?~6{XbgBqM|d_EvayjznQt1ivqmYT'
    'm|SZv+ZB0qj=U0V90XxhIrO^P7k-E_W@cty_dHZlM@E$I=Ha6_P5^jkxi<DTzSf#-m<Wdu-g9LcgZd0U&4{;q1%9_zkZ)@IqBhge6TC69#s*Z-1C#_nHS1<H'
    '6W_iV=%0B$%`||3gv#^K1c9jm|I@TtzD(QVvU3D%Hc|s{&+CMg)hX;ehGa0?6Oq&>{og|}pNM2YyF4HqR9DmFIvX9~9O>{wJQT&zFQ#dR_{n!Kz^ulciJ?ph'
    '0rONY2B>n<l_PDtj}zj;K6mgcAY<GgIz2lQ&e5|c9^P5p!#jlSo_p>DY({5kpp!{C!o-2&tA5VFV=_G`MqlcQJLip@_*%>-e-93-UiFhReBnhf)Y82PzyyH{'
    '^9AYB9f1Ok9ia#f_*>9I@$r63w{P6IgKT}IUt>p@B;8`yNXZWst}bv*1Q1I1ZsTOO^)$gbd7F<6;4>o;e}FW{`|-^!bgWFj_JrW#wVl~k7;bAi+|~o&;;yER'
    'gQ0(>{muW!-kUeKab)?T|G$X$9m;I?1xhGTSh#{LM$i&%D_RnLDcPQG1_B0wqKFX)Kqx>ITci8g-`R4lEC8hB?!FPPC&nVGvU1OpXZ@Wk|EWiRdG>2*)buqv'
    'ygu*-Cj<U_<((9M|5R!qluZ2N1nyi(lCs^f0PFFjd{|BwSx+I1x=@c~$4l5EV4a<d3=Zs)MZcT@WcyJL6E&7CeuW+3)Z&vV16$lkswe0xeQXX7DQr{i?!^za'
    'TYDNA<7MPoFC$MA9W}hXA-Wc&CKorm;ytk9R2cH)9dP5<s*51fmAOyk;sJ5)eTVi-^<ykbljvi(9|{7=a)Eu1_aDrsqyR0pFX0;07%*q3*(?Gn!HiH04HxqP'
    '0O;Z6`>xV1P=ksL3)Kn&Ag(4;gr+C!%X)cZkf@4?s}q43NEut&Qt3bBsF_GMvA&_KOyY>RzKVNSNBm-$Ll^JHFM6vO2PF=LOCzJNrd_rO#I4}=iZ`TOW!4}k'
    'S!kqvk%PsnRWpB9sADm^D3StQ6iG~&?1~?2SzX!*8fxReV*^Pn+L~*ek31SqIe`HjWvCAoGrUR2tui{p+;<!dMEUE0HVm=}T*lKxRY#g{_<n#%NP&XfjE2K('
    'qR;D5^bsZsl}z)|EQ@FrU}6XJjB+88CTM|nf0d7j&Igl<7RW8QkOzrgUNwvfEE})%TAs7^--_$x75{HzDN>z`W0Q_=zHz<O)d$or)Cjs>r-nT0E#MQZr*w(8'
    '>-hlW_HXF0AoZg|x|81ZioC1l`4RTxJ%LKYgfniD*t@9>L$}#yDJ{wS9)*#rZ1@%Uwg|xD<4&3Q#`(f9Bn)T5504`YOr=wVOUW;(9D+Sl!r_pk4A)e=af_Bp'
    '%rcR3c^_Q`UpbvIE;{)oyrdqaB|X58-S)|1t1d<vL<g%W_yl?8b^7oNonw4UKjTgiMa5K#gCadHmro)KID6XJfK^azLPBI=o@bO+!VQw9CCn^bY}p8~EGu$q'
    '(JhI-o^LSt8M|O0R|IRtn>tCkn)0QqcBFVL$l{bDj*0(YbAPvk8A1qlVWyPT`Ar?@&TKl#DJk0(`U&JS%&~!43CGzK9)6s{|0h_D(Nw=0p=KX`EHR8O`q*^6'
    '1QF<8XdqKk6GMawl${;4&HkWZ81T3F;?V%9BR%2%(ni9+ucym7%})<i_U5@|L{fwV>SOPC@`>r_G_Dr*whbb%!iy?jq*ixJfVV^5zN#L_)z_{|16V8ELBx~b'
    'yk86#QK8{cAQ4Z+u+kw^u`eD>H6n-V8PpulW9N_<bL@tIpk9xseVG}>B#pW{LzzSe5d*{nN}6?<A$y8UihKXI#&<l@E;>^*Bui&O=8aF%?L%7=0b*K8l_L7R'
    ')dB`|(592OP4{inL!i2wNVFk+BYz`?KD?>Zv-p^tMRvCv$#!G+iPhl%vL{E~T<Rt3+KVF}s%5E!;3=(7twc8YLYr7|&B-#)t3?0hWz_2@R3KkCM}pjOUF?n3'
    'pc|zp#t}-|Z51)Kw<G?p_VBqcn(q?z9a>`RDi!1vUfz_-{T5R&P&W4r0oFMSlFE2An`hbW%*uSKTn;=^ONL%2k*<OlTLoEZ_me%CRzk&lj!gj<S*<8Zjk^YU'
    '<+ROP-hdrzOL>kaz+yaEkuuS7`Ow}|$wbr`N^T<3NY~Ek^V46@{TJ>M-dyzbfB$;^);v<~;s+hqU0ho+K_LHG60E$Q4shB)@Hgb2jh9Mz208OO>!YDCkCu4L'
    '@YSONM_FZsNR}FOGIV30x{U0?&`aYT4i8_R{v82J)9ABO*ehpE_00H(+NJnF+E3_4R(EXhUIua*QCe-6ghJnW5^OTM0fyO%%o9RN>0F|$SsIv<lp6o7kQJ!G'
    'o~+H&N1!rY0VM=;M|d@>!$DFk-)a$DYf%NIoBn&WthkpK@^p<LYoy5CS1*K(okC+Ec30tvI6KDbeoG+;A-R?q9ha@pGC+wBihJDnro$PHfJ&A?yYM7&2i+&N'
    'h!Q)mQU#+@3@%6~cd*qRpwhgWst<M`t8NGC*b6vFmCaJSq^K~r{t`KS?P`Y;U5B@%P8DjF{hp=bY-g>WeIt1d6~5lF3l#2dkA<@CaAC6#I}w(tt9UiFLPvNl'
    '_X!+@1QNUz!ZNG5-Y|m1TD8NyPT5lI*e+E1SQh=KqL2fX%O3bKVb(Op?!@!Gq4zfI9&|XeVmIgaK^G_N-)7Rj9imyfUmmh&EaI<743NYAVll5;QwAhUI~K7D'
    'GA{kxw7jZ}-bWj{GpQwXe3{5KDSEf;&xai#c5`;uAB=MH34#^6k48iE^B<rZYs#Tl3>cjc;4DsTw<f6i<=N?*V$hX5wxXl-v$Knf^NTl(*!UF~o$N^!dDVsp'
    'so*_%eO>DjxRSUyje1E2(et*kY6B0nbMD?wLb{QV8oB(!?waHRn{VzJu%LxGS%vFZmf=7WyL+gQ&a{-B4QBxo`*_%=!>I(L+sCNlw0#8wOJ0cWExPtO^-6)%'
    'b;zsG!%8eTl{V+9&?wR34@ct7bTp1Gpzhl%)Ye=8Q7-VWzqQ(JtuIN)S8y`G^!1}p^_;>Y-<+XVku<*d#I5EGpU$|F?Ui8P@Y=(nY&#kdYN5yI<T@M`y=JZF'
    'FgpFjNk5$`Oh<kv@G2&Yi2Iev^`W188O6Q&2IAsszvnkPP&ZKLbq37a)$+c)m(#Hc%C$b5FQDgRcG=XAIbxT-p}WJY%mAqC*ZhLv=(#hdBe4xs+3u+<T_h??'
    ';*yS=Im?`MM=;(DC&tN*rNFYjOPdX1yMZ?^&vpgHK386&A?P(hEd5^jqN2<Ma9&B3tI%w=i40V2z>fI16_JRI9lc~TQ}?*lYB*2Hz|}q3*$p>}LU#Z|4y5mw'
    '=g<Cj_Pnw-;oE^p^cNV9o%fVjITpJGE2a@E!GGjG*E%Y{8VBGr)busyX)}Fnwvx7!3Q|MYaDo<z{e*9-{AYq`<vYR16$_AEfQbl(9f#q>u?Sp|hSajn3xOz>'
    ';wZd!2Re33q2~xd9LMsR93fVWj*b7KLvt?sZdg#a*0+Oz%DN*@SleKqJS&Y*Fn!QUZIzul@#qFPaQgLEl}3@c^VUwQgL)*6U*}p8${zQ(GQz;C(ExQ${V_;I'
    '!}~~+Tc$4Cp$sb;wm{(vV#dCb_)jL?;q)wyV#_p4`vk{yQf)^%e{fR)@<}#9<qlA7Hj`#6W|z6e3aS=|x~L+aR_$k{CSxCnw53wQa&Os*B-BwoJYCp28I+Sp'
    '+QX}fw64_~+HN;V-;D`XXe;hnlA}b44OSkKIFT@))XOf@I`+G9obGk>NcZ#zXf@RHk|d5RI!42hL0n>8wPvTg(YdzUSbHCB64lBv;51go)w+Uv6^)qXGb+)K'
    'irJp=?TqV1_)-NTP#AI?xC(XBExSYCrK<Yi98X4zQGc9zc{U3Nit&A_mzRdhc9S4+P4>E7c7UXsdE>$mYL{M2p>p@w!-{Bn%pdMWFOyZnzo{efiAmtmd0@nH'
    '2qtMX8K76vyL7L%_e44_js(QXrTdLWL%o0^)fF0LeapwSraBs2OO5shQ-$l%RdvFvIx%;nEF&(P<jU?QfoIP8)>^TR9}z@E5^^{V1ll5N;9Z}g87&r7>*(Li'
    'GL^Mdhj|{U;p-=>ClHO-_U!4ToJ9b_M>YOg;R^0H8VO?!V$_WI3w7F!#ux5GdGl{5gL|lI3Dapdv>Q{W)zF?y(4^zc)IraD6~A%dwu|>8;n|=|n}%1YsWG0w'
    'ryib8+r*cJ1r5@*9fe6P?=vy-9m~+FFd2=)X~r0Wcum`$2vpj#kK)$TNqIv!*M!?f!FQF8B5So~QjzW<mK*)?#lQyn9djf->{jb2RIDIwVbMLyy_?$U1gG7V'
    'I-Mxfa`5e=67((`RV;|%#oUR>YbcovCAH^61g{|0f4OOYHqFyec2H^`(|}@5fRbDQ0<^1iu5j@4v|8OsFb;H={<}l@Z!te^Y-O#dpl&K|Cvu-TiQH#?7WWyY'
    'aG$A)9+&B!0Y1r_(?MBK2#a>;O>C!l7we)q)dpcw_-oYrR$DD)(?R|_O<RY2*jnwlu6o>AmvO$BES?%ekXTF<uYM>JBcUO5FTn+2BlHKvPzxzF@U{Rc&O}yZ'
    ')Py8JwI}sdsMr(*x2fjL5<S@t;pCd|iacmmTqy5^e2KXeiPwsTz*I|jvz)w}-+#l&x<+#xUFq@aY2ucPvm_kUs#(%S9yLqyHO><Ep*Ts3+tDCI`Fn%dK_0L)'
    '8f#o$G6{ZK4xq2{w;E4hm6>=n)&^IVWt0T|7cZap6h5_oi9ZPB`ggkKP1Vm|{PcAds$S`(EJ6+k0E-KU!s=2fSop@BD;(LdPYwegn=PyGGX1S+_3cNTJ`ccz'
    'x@GDEiezfEJ_X+CEchvZX1ihApXp=@csV+F22`R$yHi7SSoHssL;3Gxb$xDA+Po_NQcqR7Sj$0+Dz;goq~{f;tBZ=oN8tk~jo=Y<aty00qw`H@zEq+N95xrR'
    'BkJ9P`p5#gu<(?1nr4co@K^-6)=ru`AyGmQ$5%?!Hntr)uB{gLirT<%dd9?+SBnV<iLG~%I4V#a(%$hNkDct0>}32H%|Z#oCAW-#TPj=HH_z#9lBvi}-!T8S'
    '+Ra{8?9gdTH3_h`bRnmP+#h8^r_4ibH6Q8GAoDrTCQIIb0(Yb7_$GIJ`4#_AeFd3^`tP!ohgX+Ls$1a7-dxDZZ5*plkJCMNQnEC#WZL1*BH)NBdJ@DaB)_6`'
    'BSnbr0)2Db#D-mQ6D3OB-V^p&LInVIF(3r%uAvYd=-h(@ErW;@)K96ly0Is*TGQ1{H<`$Cp)_PxL%GrY@~a`7E$rj=rk((+VV_+O*MPa+u`2i|&}|z9dLxHA'
    '2M4+r_NhxhTW=*BJ!Stu2XRH)C@CQ2ucyCMX28!9Al7i?xlZHD7hl~WSkubqiCQkC-jW_#`L{ygN{%}>*_VO{OW&0sELHy;bfvJuoJ|tP&E~2*ujtPq(_~+I'
    ')@D(cpAUpjN9#K>1=&yV!I6JgrJujp&zuL|S#9`NpvpDu-GRXi&`xD6$KX3!-#XDXs_=x8IfZYmIHZJyR$$jE?zN*-3eV18zC3&Owr6iedtY+=qUny@vE;%Z'
    '7f>HPzTQcTxc+t(HAdaEW(B!AZqz~FOa*$+;jp!oTlZYh0+i8pYpAHPAUB3{#5$5n$k(Cbwc=!wWQP}}RZOf%ZIe#Ywo#K83p&A9O!ApvtUa-yc%XHTK&6}P'
    'iYLGdO~y&OS47U_wu73+fWL?r5<xOk(L!{rd&kPuZcQF2^Urbu?074#H#?;|)D>;!fwVi}2GX?IDb1p#&-SI?-EK-uu6``+RHYk08|=M#X^`XXgq%%ZyexEE'
    'BdQt`O)KuK?OkouO)<aZZfz8F(dcfn?LD6(E90j(g=I5s?Yxf8t)k3&92#>}uD)J4b7UnzaGVTEvLCF9`-qF8WWnb6P?pY@k=A9d6d9>Jd!<_;dcT%>1P08n'
    '%{uvh$k%b~rsUMO)3*`CeD%M*B$gTA$P?I7N5xR+o+_oH5SWWn_lwfFB-S0!k;uap_lN>9Sex5S_qEYY^xrzWnR03MG!}Z`k`KrBx85{wjvtr2R?%<sp6DIF'
    '91GN~wh0<#fiHKkL3JgZt#OtOUZaUhFYDni*L7b!Bxb5ldnfrFijOTli;n<RCNo(mvQ#^Tg9iFqPX|TJ+YtTnT@zQ|`M#$jCsWo96-1`q#m-)jF5KSfPmb3%'
    'JwJVZ{=0HKML?n<qA+E1f-I3jmRmO|&b(5jJYxplQkxZ|od5{FLLd%NLZkfFi7)*A+6_DIvJaIK3z0Z0fNkqdAK6x;l#olGwZ1MV@xE)jiEA%)cX7VXO<k{*'
    '+F9sn46|)JQ|mG^s8Bfze04+b@vwimY0LKwx8(6s$MC|}_H@R<-Cpzp*OhGI0gk~q2dxgeZo~1b3lkpQ-DLg6Q&c&TDQdP{sPq^|aC?s45xNh>J@zHkw0E)F'
    '?7evX%dc+>p%VIq?aghTIw2JLDN?E5&oBN4WGZbrZ=PM8{{odLFN|s{*-7?d<B9<f+R09A<*R{DX$(D;+JlY}r;1S?1`lwXT&MLlmUBkBV9r5ZgmJgVk7trl'
    'zz7@4xUStEy4@qW+Z|ToK2aGmjjNyQDDAo4eo9ojO!EO&Q4*RRwkS!`O$UQULo2zf6A*v32rM=s{Jwic%yfcUlw{DKrG7m&u9BN(5Ei7)HQ~P0J|*Or7+~;a'
    '7F9y{&)j~8ZnVnPXui0qbOO~SY=lzp9E(&5%o#|GP?*0^+Tl6;82yv5zTq#b8i{IBxkGT5Y-pF3M@q9u4#BD<Qyn>@3IIVoWq2kzby|lev;s2<TwH(lWit<q'
    'BTS)f=VJd$^qPHtWi?rsl_9gt5uOYJlp%u-rPSpZ4aQS~lNO4xZJCMP)C**D-fy;&DvY(Z6F+I~IC)CSliiRX#R5d>9f3Hb=iQ?|r)pSqJ=b$$lf8r~zF)SV'
    'S0<RLK_{P&%Ww?_C7b_~!iqrqqwvadx>IF{#1=o@7o|OAUiUGa=<%iA5nXL54<<^KJS4vZ5x!unMs<M%ErBNOr1K>S5%CpeFg9P6WCrJ%;9}(D?etb{`fltz'
    '7P<O3rO)c>F&|EREDt0(pi`USRTuH9p=;$^Vdm0eq6X#q|LPpR2_;1Mlnn1vdV7gwyGLea(@W;saf2Tw<~bCr4L`+kQu4Y9ukYj7+rA~v&c*##bfXURTV-IL'
    'bx?-kJ^29`ycy@gA^+oPZe31HIKC8Xf?{gk=|(Gc+>(5=vu?t##o|7TV?T{dbx~`gT^adJx<N02T6tz|IW2+v9aVv1$4}5)_OU;<BTMv23LKe8d$CwAk5j2d'
    'vFHukQyQmF-XAZ_1~paVVxS_Ow=`W^HO`7l4^Gq<d}UZza^B{S4N@)n*Q?ijIdyB;5vGXTj$bc3bgrx3LSE&aNux|uVZ2Scb=3zOc~wvUtiQM+)=E}LX^d#K'
    'H)pU^clyKogz%%%-h8hmZO{YTd4VfeNCXsE23s3P(M(oZE@$1i-m-Ri0h&<5F{=A}o^q{4yf<52ka!K+Fp+k-ZoRn|*IFhS86LzAD)#!sEJS1pO`>=6X`ZVe'
    'nA0%2o@a2|!dfMf%J4;Kkv9oqhYU5|9x?F@$(KaJ%hNAHo?_D*&axy*(1?DOT%(NO-KgO9vi@y)30tF)SWA;s<Aj5!iE)6J+6(du4uR#+ML}X9!QB`h;J_wf'
    '!1MM=0e|UHzkC3!Mncn&Os028E)yCp4VDI(Xi0^-8IV*z-6sVfwSdCSqC}s_hL3HOT<FA8@$pZgUp3p)=-&4;{d8}<O#NUpuHyvB18_jKR(nN*Na4~AC|<B7'
    'yyNkM74<WVu8ur2>6l)Zraz_s*072v67Cpa&<S)AKEX9g@jta{l_n&iNnkaScfH3+pvP)QXkRYfk$Q7`_lY@|Pmm{5O~#2Xre>tpgr*Z!poDRE{)fx{Kc7F{'
    'f8qUAtKyh#9TkxZff0#i`xQzFAyLHw8Pn7d{X9^5=m^hOwJy`VQ>~NAw2s><0ZthIv*X0c(@9k|Ty_pz#~nI@Cuz$M*+<k&)H$U1IkZq<F7Q0tw`H}izo8D9'
    'U(hl0qh<eqjviO*SQC9he?V#aw<Z5VnGVqo{h7YK?JlS*8AKwj3$Ow*8eg1SjrbE)z4?Hi>~+m&^kBamQXWW7=u*eI2L@c01BV3^3<1-6!KA)2p{P_4ipnIv'
    'CCdP>bWhlG`2R!<6zS(Li88N}<jHxZQ^(s(JfBoR2WOtPoj1xnfL&eW1|F@YQuPV5S)GE039n*VM>e-nvf0s~kS9zV3QMc7KGcdv{kb=IeV@6ruFTT*?X$vq'
    '9ft&36tIb17n@=DJ_{O$Pg1I)Xy+991*<;VU<xTbt<2C``aRi}3lnF2LUea*Ti6Zq48v8%!SL*CU}qD=@74Z?N9$u@2Djv{El#(A+ZX!;BJ8w3^v;Db&;^WG'
    'GIY;P@aO{>jkrpMAY3WhiyY>(nDkJ&?J=Yzw%6+q{~Pu$&?RKGnvJ+bAt0kwPM&r%AG$~GP{kBowjsEfmFcfkvGC#8A8`3LqdD+=82qp69|8{O+T-1wy1+be'
    'I6PO1%tdffB?=-zekvi3C$+yoEY9_G@oV(7-=+Ak`^HvuLILWQTVgGVEoY?c;SnKgpmDm4=~SD^b9yIbt*GVnLR8A91gl7$q8*PGYfh4CJ__}6Bbpxw`}6-7'
    '$dW3@xJWos=y@S>M@l=P^ai^iX(erqUC?ZiZs9m>9XuAR;OOh((;pJUzb1m82Ic2q4i1X~r1SK$_ZyC@;AM)IwWP!Y72kE0oO~)(MYsKXoPCVKLYOz`I%Rp6'
    '%+-|e`G}IgV_pk3v)?Xrgv7t?>&(&HwhtvQRx4>9Xxx=q!T!sET|tNpV#|z<LWUf#2#}b0>_ze8BJyhh3?dx35o~yRN2!0IsDQsDCTiFAv9LSQabUX<g%ZD)'
    'zN?$sGL0G-*lhT}_=~b&0xI)A%--ZSfNVDW&go^ysV6)_WrHiTB&zL7MhLipwM~&I3`WWwQA(EHhqNJo4W=OAG>+g_k_51;WSGrE2ac4tV7?|7bIAf*xtLpC'
    'diG)@jRe`4d=bBL_J_ej*@xuha0JbE^ozojK~<CB%AiJzQ6Oid!TaS*Yp?hSV#&dBPREn?PK8<^++*|wd8$X8s8+9*_ZV-wK!QoDrLZFXyyoRRk_Wa>GFzPj'
    'D1T`VYe)0f@jGI&M*Axk2i!aZjkt>wZmX91m5ba6D<HQ*>SC>QkL0r8rSbRFfLxzUw)>Vw+A-KiR^=<LZH024-OXyIBq6#pYK1pDoh@fFY<DPiJuR`hB=ba$'
    'X<`m(VvcBUzIV|3?<owuN2P5|fYNv~Y^m9k)C1QYlD_Sf!z5TR2q6+x8+AysA-6Rx<hYnWd8{2$R!Lws8$)JI`m~${(yqw%hcaa~8tIx=71ivKRt>+_v#TSC'
    'j@Ez8>Nf9lA(|=)(JE>2NONM^O^>}lOOH|FjI!HBpc_W9F|MLCd)*_SefwJ9tgnsDkw_fh3#S;4vr$M+AsWXD_VJqtByafQ<I#Fct#nU;O`0On2`C@*b4#h9'
    'pA~kj#z1sMe_saG75E~gei0G}0$sFKOe@+hDwK3x-cR=k6(952Z~(iUr6cv@kxnA-Ic=?V#`{*e<Nx*P;zN4eplf?<`xln%PlNdCO<=*bFNBA)(xb72_*wpp'
    'exK;RbV?Px8L0~o@n$T#6?&~c#JNy7S4LXq#DKtG7)Fj6ewiZeT-0AKrnj&>12kEnol|)k{th$!^ZBm<P-f?)<yUCw^3gdd>)in>34O@zF!+ZWs0GR8udSW$'
    '(pGyzS^O_#dIj-dIcEM>l8tJ7^QSTyB3@31*|>uf2aFX?T8>#)5FmZKME2Gy0%1Jk#|d?~Q&hlMikS;uzdpO@y?%39!5N%nDyK(vg&$<%S}Ed(M!BOCR%wKL'
    'SD`CXfQ0QGNsOmzrO2XN93)A;I5v>AxS~tM@a(4igPO$$)^WPxaIp0Adm(1zFC*neu}o^p6B7lNWkZ#P<ULeXhzarh(sVFHXGMTvNcaekOhc3EEMaKT4ydW!'
    'RmL0Xo-V^4F9NK!y(uL0WB^1L6-Yp?i8^cF*G1~aif}C4HxaC8aGXvJ8)7^)72^mGsJbbyTbV#Lfklxh4*J9jJJ&MK2f@Uh(1jIV2;(z_I%8c+9p=I?{nXZR'
    '`tT@rfzj{-GZZQLX^v_qLNm~|@aU#*gSMjQ_Vj8zddDotQ8WcwGFMbbC3W1^s<7dZ{7KM@6Sm=Wh<Q{=&ZeY}Dl^*Ey&~N>d3DKGFuS?W2~?lu>SA<_<eIC_'
    'j6O)X?Kc$DW@wjk#j(S1V%MpxzAD?#425`W7kyaVld*)C!t9b_IIBt`ySNW{No1cWL*ly>#nmcMT@NH=tr~!1f0AO-U{$m2<JnOUVdGk|yY&>dD|9rZB4Est'
    '<7T5H%9l_q4}9B=J)387&^%}L6iOe_d6Q5d{2jb<(XmXfR|(zGQ9Dj=ougst%k}dUJLY7idAn#tM?s8~O?C)Mzz4b3O!k|HKG%4?#9T}p`W}1gzpmqc?A%J1'
    'T<^*&&o1I!d0|JTHEI!qy+YGrYk^7?I6**c4=pFCd6LG=xv)p$@Eo3fM5D9XDkdLxY6E&~b)6_3>#RO7!AX>J>%zXOXWwbmpT`h?sTF%0uGI7hIAZvkjyvT;'
    'U|KA|E=(nb)y*UJ=LgOY2*Nv}^GbPoJ<<xzRiw>KTjE`f=8Xm#txM&c^BgX(I?vuos#^6kCVe$2)W|UbY6xRu|MU=9#M9u?xPZsQx1pz+Du#)unn;h1`b6{5'
    'L~`wi#w4(uz(P&OA3361G@jH4qkLpG;yXd*>a49@R9GtAs)ca+l@K*L5-=dlt<^xRi(J$q8|VBCj8O^kB_mB6NpNYL=b@Q*KXj9;{a>IrQL9oSC3~UQWx<*2'
    'H@l<AD6EYHL3yPu32fz(I(iv@YnAF|%3~=5O|4gakT*3@^Z8;r9Rne}rG!+oY<|1sa7kdMbJRw(d-g+8V6=NLPk%VSaPr)Y`&ZMstz_f}3>Qu*L22*t(|p#y'
    'vvi33(9UYZPe5dA?K!{ponHq|s$l3Azd}an-Q-q|x>B1N>EoM6QHmK|2?njbq_v;4*qScdmy=d8fch`dbIw*T=}@D-WNarXp$^he<_JwPxzXKdaf7MrZ{a+`'
    '<K@Koz(k9zf9n|c)3mj3z~OXd#olm)Kc#xG+GONkEijK*NBp>uQ45N7RE%@`Dm{yic;gNhG!Jf`lu)o#Fi?tXyBrlmrSzM!U@23;4VPLU;D~3#0M}aSD>hB('
    'P^Ln&rr(GccKtO@D(3hz0*RfJgI%u*&XT1lMpK!Ybpo@vEl<oHouqaTJ3Kq;JNZOX(Sc|)!<nUtOsaeI-+lV;0ZwgFg{8q?hZu?t&-UoqF8$i0|L)_nICKVN'
    'm<Xm5fYL#fvP75ID=DFri#Jn>0J=o+51n$5Lv6L|PLdnaylFy4@yk9fuJVXoEEXibh2Rtlf<YHDtmmJjS(T?TF%9_KsRK<;-xHuYR003$xDkHQG%pI_BdQ(-'
    'zQk|(SkaZPqK}_n;fFlr<Vy9C!XT*PW~UpM)=PU6V_2|cz1g)vbk!q5(zSiRc~8cELO_^2wY78u)i6nnDV~F3Indk<w}^GYxO*5W1JxZLr+UFVvJ14gpDC5#'
    'RLP&#3V9iY`12wiN5Eh66-|$nbwlV_^9lXWQ&T(<>LdHZY)}1{_OvHjVcn{!HGal7(R_lRKks3Txa(_ge`8$k!=NA@Acz42@mZKo;fVzcVgvzqJZpsj>x*aS'
    'uYP#(`s{gt1#~MdvVSXTDfBvwz7eQ_Y!LxY(l58E0qwBeiG~>m*Q201i11E|Xd8)>lxTZVS+9&}s5!_c1@EeD#nG*cr`#~3#5d<&N+R|D(>NF}^Qh)YN}|7='
    'w`<s%U?liv*)#qWhNf4-(9k}qHUD&$#tM(wfVYwJ>5Cq<R>I|U;?x!APEN=peZ4l##bQ_$GuLSDO-S?CBZqzG6jT}S!;eySlRl_Rg{~lt3%AY<m4A@+%2t<e'
    '=A9bge8V_CJ|mPbfyyt^&!6r)3mv4(AZjuUTcfJuQPb4S&=<PG;4We-n3*{S1yS|*iGneBSX}yw!Ry>DO%5^6M)M;DJ>!Stw$ewI9i>{UHad~Kr2&|0y?<)T'
    '$4tD;P7ZfFfhYpT<o;GM=+b8WL*4dNwAr?_`k_{(mwK*MJgWlnZpAf|@r?MjVm`CDHu5Ux?M9hao|FaFlbLG8U>IoDcmeY7iH_{2@5w=u1K(vo71xnEbBtld'
    'IOf`JqljN_PE3vdgK4uu3q*%ak*LocUecjGXTpv;9}*QB)gg$VFR?nCwe*8^I1%VBU)Tq<meM~(3scEhJO1pXlR$WUau2*MyD>sfJLUu;aink=UrkS8`DxYa'
    'S>5uQwH_z-^SbdfP3lPQV(0pB*me&5U+<W!@zXXaOR8~c$iAIEc0L+BWw}Jw*S5)R(!1DixX5SlJK&oHPbK9a0Udr=+}n4KIA$l)>uVrRM$LwS0pe(}K03hm'
    'zCaD|!#ptXi}*MMPB5K`Jz2JQN@XuQ?e39&Wb7^KkssSJ(_S4kEZ(hY8TzHJ#ZTZjTNkcSa9%Zy6`H9bFQb|gh7GM_0YdJ$(~H-ka;N82t2G%8RDK+*qd*y2'
    'iKZ$yCgUSz)wbS$eyz8ZFmPxXdblsYM#_DZE55T4nmCI!t2gxxgH|cO1XpyjdNmxMN`2xm+K<kdxPk_gCl(whn~h@Y&BjJ8yj%9?MGM*{->~J$M8rzN^=88%'
    'QtG)wNZ5mt4t+<5H<W-4gjMy*rCZakN2G5k$=qO78t@QLbo>K3rOu~l6zveW%$MNgDT%#o+S5j|dUgwL*-mlG?BZ@6%cSDGaD2sARIE)jt9PWfAQrv24K-Kh'
    '3k!NdM^1W?cA7{h)A2Bs51lg0{@9KbT9pjm$;{)O*gDi7Z*&N4_;ZKea%VQG#0~Nm7Y=n~oO%jTHkU5Cm?ZhIP7^6vN?||BPZpYp{DWoOhmE!a_qYJ*mc_9a'
    '10%y(D^Puj)p2>Gta;BU4=bU(6vzZ2)(1Ouaz4+;F1phfs92*4N{S9T%)#gp{gMy{;Zt8Jo#h}+z=oX`qSNO+%~r#0K#mSmMC+u4e5mrUCV+3X-6H>Q>J_#;'
    ')|Nf<igjo`9iuCSV0MnBe*q7zP4}$SP>0%z0Pw||9ho#8Ku#`N`1f(@OQLrCHmB(>IR2{pToT@?TfHQgmlIs*i>3u;Pt{^`7pk2SceC;dv%}8Jy%*R^`f!^x'
    'fG+LBuE9jdv0>3&P5Q%i>3q2vV*&c9$c5)#$r^vY)PtgI{Fdv4x&C-(28vle6I#!%$N6wK8-3SncPf`Su7c+OSBx>h5*Sl}9(M`!cEP2osKD2?Z>m7tKkQKe'
    '%haO4n8RUlL!cpn$P*L}%JQt)$L=_7YhQB2RoPJESau&BT}>y;+|HQ9xCLmv^?{^4yQ@b4HbXIaIC_artsce@VMvt#e)AFGmZTd%ns^oBgs@$eiX9J$Bpw{6'
    '!&<XW%^jyrM${adDZyJ5kx|;7L6NFc3r6Z5d95^AX}OBa0=6uNpOooI^mmu)QMblpfwihDtjUK0T3WTb_>~QVU-`{V56qyG*HOBGa?vqOwB1upGr)j_Cu!>m'
    'NS_vVV9ja>XbFaGY-pKlHTOCpFnkd3qYO6c^ma6eFx#IOp;1R~Li7YgVu+r+e~F&)4-BZ_gc_ab%_2iz;g?w!{fug;XzS&4K8#*XZ>P}(jVs?uqBrnWc6*i0'
    'o2@9H^k=|QaG2b|ZV%IPMyU`8d2;dAeZoW$p6L)ec*q<mJY;nhJYm8oPZWKF=Qui|W6`5S=qP5cp=0J8zpiEpnoSA6y*U6L1B<VK!%=(i0hl;gXIw^!HGZG5'
    'l)6UJ<VnaP`fX$71Rb~JicvxFsYReHi!Aq~EK<!Nz7&kBT;@9`Ppq9lPn-S%#GUSw9{#u2U$`j_3Kr9149^A^j7s)uB9DGLKYw#ZY59KF8MlM!{H`6OERz6M'
    '@+4cA81yk4ENPpeL*bCb<L}Z&xYmaW-6l5TI9wrT9pq7UDrZ0aBxCDTUcGqvH$6m2NBHHEZ&8^S+tAHS0v!7TPGL&FNgpn=>!8jeSSOL)>NN;d6bGo`V&mFw'
    '{G_?v+C52~mpURKJTbUL(EMJHbe)>?6!t;jYd<fRIyHLF8!n1jNlo)G8#?OL-;ZV<R3Uo`(dUoOPW$NOSOEuoBFGZ0!8CaTbkc7@OeyRs^@5;|NUgvrR<JSU'
    'pVuGUWP)#*XA9_eABIq^2o;v@vxdXOEnqF`gi;M1JErD`{^0#xAMVC^#z;W}jH;HJqHDxRue0=3xABO`*B99kg3{i0a{o}=7|i{X{Z@JO*naZ>I7eh2eaL|a'
    '<*X<~i?NpB5m-Bq$!GC6WxnpJ*sj-sO>KfRwHC=JE@UgiWrFETdB$qo0sXv&&XdwX+scR==#uANMK`Hf@*!eyn1t-)t;Eo9csD!}XU><QT%{k^zma|~e6?Xk'
    '=4xA~0K_syT~~=*^<bqN7b3-5yousXLf^iDzR_7fr2tkcHEAX;BJJ9<Zy@tvjy`{JvjN*#IUR+n)u=WT5$4!R$Q?u9ig>l3pF9!NvcjfFo;<1A@4PO@U&^(@'
    'Si86Ah55p>>*J%w#q1Exoy0ywmz>4tFyV08xLeZ|$DXvH=FOHFHoB)uMTfnWXd6s%(h^BiSA>*^pT{SuNsm|rO8ibN)P}UlXJI(6O;P)}{0&@G)<Uech306$'
    'SxtE5zAGiR0c<*3{7$h;b!?|z;4W<S9>rTi`Nu#UtV=rS44zu)Y9C;SOOxb~maX-uq=dGqQgsiCX^b`qYSd!&19hxl3G`JovuaWP&%pZ9m2ZObrI$fzW(`xF'
    'HWF{`oF~dcs}w3;-o`aJSF2+$om^UY(8B?k-~H<XFr7VUbzSRoOpvCfeF;Zqx}RRW^**&p@ha85i*%Hxt@bwx6fF_AN*0<70%jW#Su88+7zGMj&lm;tL4CYY'
    'K-a#p&Tzk@z>wKFAEO&_%0L3fJ&7hR<XIF5)^L;$pdSdyGQVeS;(!57q47Q16TN4r&wf7hm2<wBEFiXzxMn%h@xV4XC>$$X0Zegqhj5hR@$^oEcfIT1>WqMr'
    'A@rLm@20m?Sm-+fA#WbB_{qYRyg9+Z%n&q(EtRUm<_@zA*52fH0#4}ZB{}1Fj~Iv#LEP5{AmVD|c8W#C0p2iHt;#>Yv!O_-BuE(wW)H%ey1o~$)*?PaLM%Fq'
    'Zln=h5pv-tOyqA?BqhSc3%;7?XgX6`l0vc??NPWYeV-rKF`e0QsiG*V`g!`w^7l!&MktHX*l0n^z*!gpe43m1xsndkUX#w%zRt{Uc}#++M!H$*hTX(TV}pLw'
    '%OLOtv>urAW`}k@`F3D#!BstZesTUwB`_g&lXj58%6Wcy`t0m0r&(s%8Sw)rJ}#ai<A1v@t)tq^^Z{}2<XpQl#p5QyI3}8g!VRmlm9aO$a3?QTm?@!p*l_%|'
    '9CCUIJ?W+<Z5(Y5_tNDsA-S^x6q%}cfT`}VgUVW{4RsEgSlRMuIvL;NYEKww2RnkGF~e*y%8^SP^fAWnTEHuB`Px0`{qpnan={*zcF_Cz{Nlww&R@F^+2y$R'
    '{Pgc+PE%_52rdQK7D>dK_^5i2L@oR&y7;KNmqcyOV689o6196|<+l{fAlR44gN>m{zZYTkK7EG}$jWe`GG?$9J$CP1s1}))TGUi#CB%};a(J$boTO4IXPH%x'
    '>-;p1{%UnHRj@*$&47CNe0g>hd5s9S8Baqci5%BpYi*SCmg-zF%MvuxKtAS$%HIIIOMmhn7%W)#$#hZ|j6B>1LyC-7Ds0$4Y1G7TpP^}o*xiqr-e4$Ez!Awu'
    'SK};t1`KAD3F;Ge=pOaY#3X0KZMWyLg&gJfTe2$U+$!u)prFvh(;wfSUFg}Se2uEFoS=dyU-iPSaMr&Erh%%`kQmN56U=EdxZ%te)4>236Pu@l$=kNE;ef{k'
    'zCV)n_Q2ib<+0fr9Umr1iooWp+WSPkh@+=Z&0eXY!uyH-9d7L;Y8@7m+tHf2p3`a{)aW&zH6k2PaveQs?RBskgyqtxhm6uiMuNL3-b6sbK)QzYGx@UTqg#aA'
    'g1Nt1-V-%B3>o1MJ(IgUd2@#8i#<;N(9z30(%iFo2Dzi4xre_G+kAY^+8T<rOakP(hkNuFHKkWepuM>N?orNQ(6oF2lJ#;7r-0S|bktE-u)PlF&(Txv9LC?+'
    'Zu519n6i}JWpI8a3@y##BQX9pPc!X;vbI)1yKUS_I~@h{3)UuKZh=2?K!1y+6!_1Dg3816JtQ=<n}#OKIV>SCD?s7$n=G3}oQ(%z8ny*FNL4k@fI~oi5mHqG'
    'GxTI~ILHYypYKLjqcQrH;)-hcIUp_XrrWN2-(q?<K`X~{!f3qc2#nTcVZ<tbKfQR}d-L`jc)Qq5)Tw4}j}S6GQ@ZDp&8{}NP78gKHd|jjoC=v!hm-)-nvC+B'
    'O@Xlsjyy_#fDUrObU}=18_>ziS#WB!fG1m<08g?+Dm&_=;iD49VN7nFn5I9*v@*9DV<s>~U(EY>Pdx3<uSW1U-0(U2Ay1IySx&?Sz=PuspNEZl^M4ES_BX_@'
    'emwHD+H5ZTv}Z~2FsOaU8GR<$>|eN1#Y92Menb_TesnFwqh#t%fLh!Dh&4xx)AsnTY!3$%ApysFCYeXfgrJLBF;GzkQOD`9sVn}jrRqzkm+IlMs;X#y=Gm~a'
    '@Rl2Q3I=<}(t`kAt*-6|p2L4+^C>V3*({gKo;g&Oee<yfs<!YBa5b#xICoT`?iLQ5#clyVqv#*r1wG`~3c-8p%4_qI^zK`OW*+YTDNvcd&F0WooR>{aiaRYl'
    '3x!u3qGJAEVwur~5dY$QgbAc{Pg(YlL)ZQhEaw<M4$F-nhhJ~}IDDw_qur!jAPZEdup2|P%#lmFW>|TZ=uHrW(LoDk)#Zdyw6H`!zX1_;NP-*TY${pW$YBV_'
    'x|}1B00~a}g)AZP$cn$G-!D(!xY78B+996o@KxM2iA&h6;Cp-<9|0$bS+b89E!Iv+K^nD0>-;vkD%MBaPpmNeiFGqf$^+}Ya4p7-PD(=T5ioI8Y<&F#kMxp8'
    '*R^x@J}wg9?N4c#{pw!TKF~UNozk(Lh}eVg6Y9FN-b3g$UOH95^$~7kGJ1Ct0$iX!<D)S`q^Pw<rWK2O9$za##5*NO9zLpgK$!Yqqbk6}Ec)*=W&}2aD%czb'
    '0c#GYjXuFwow3dfkdD3F3bhY)^R=@MSkhU6tL2bVcYx&K9*p&1N{nN~;U{H5B09+h=G6hwZ;?$1>YQ-XGz<>{^}^nr!Sw^Ah<rn%w>KGT-c)J~_^6>O16hvo'
    'R-$)^!A34zP%)PT(Q#m@2&3f;E2k_PC{w~lWH=wCTNDrd&$CW3Bxkk?2WQr;x1duNz*;zm#+LvB2v2p<V~m~$=})Rm5Jft}770eKF=0Ej4lyr}1A<`8K1dfp'
    '3V5zQ-qCYhOl$$NpwE}0n>+Wa**&t)1wU+c1DHR$T}7Rw=?_nAZ}mWWaQ&eWGX0&_@V6TcakJmSzeKOU+h}}QU+Eh(#aUGf@>bJ=-fF?$DkN?f>wkN3`uh)O'
    '7Z-oWa`52Q*~|0SmCk|No=Qy!RUfAgxRDt2)dfruN^nyT&@e-pU*HCYI}62J>%8Vm6xB9Pp|v_vJ{%dev%?yN<GsV(5c9sd+rZkC9;`T7mDhty6k>C}E~$q)'
    'k?1~wE~#re*jn4cR@VZe5p7E#4Tqy`nawlg!P17~6KT}|B0{sFttwi_L6oLMj!g=g9*q9OuGu=uB<{h4s>xVAr*5fIw*}D_isf^VcOH&>ldsgpy6hG=SEZrE'
    '9W}A?RBf8L<`i@D!}2H2WS6#Ggy)IBPU&W4))3G-j=NcPJ&UlhuO%2J4Dx{su5<LwR9<qr!@90N8B6p}RceLOsVSc$wu^fJtI3nw{)~||6E|HjNCwD{rk4BO'
    'LjXlJKU?s65{VXbqqw|oIa{&bk)hyN@Kw$WR;ITH1=B#?ylDt2TQ#J^usFSs?L@LV@siyQ>;nFg$QgGJKE4SbUXC$lQ8dv%Nsj5IMPb!bc&gLt)kc{(O>Mx9'
    '=cy|Qc@4V~k+Eqw6?)p$leBD9E4{*j_kbzJ&=XH-c%%|AT2ZRVkBFOnbpUHI8d~uLTDGyoz73|#)MIULny|n;l}`_~-oMT;QFRqNz>*P7%m>jPf8f(%Evkm8'
    'Wc?R>`r$Zr7RnZ|Jdu%J7jZ6S1$YcJ3kh~ii7`J<$9Ury!xh^;h!G^q{<do*QOA6Uj52kT6t-F_lFotvB)T0K*AeV;4it#cW0&TM{<?;HJi6`QM^_jUwP2Tx'
    ';kKtgF(xi1!MsCa3c>TD@J6&D=)EWcl*ZjNP!^>de}Ys1hiUMLaC`diGAqqeJ+$|W5y|RHA2yUjIj~J$SW*`?0^dWqkVFPw`{QkOkBW~Jnj%JYsJ>XO5SB~Q'
    'D;amOH&BdXWbiX@>>ytRW~3A767)rRA>qvTzR|2BzpQ54W-xOOETCGdqp$%-H%jEKENz(tuci)q2#rf}qK$l5WPji4-r)9iH*I&NnKP6#P0omg&r`boY!vff'
    'V(wF!v4G&M`;9pz)ejS_6Y6H7sw*U!3^9vn-r0avT)9b{>r`#e&?Y&iTWK}-8U}|9bxH@PyG*j~);D64X@d~ou%<#OC27ryz?0=)XxkNUl+e`GSKjxrlN<ZE'
    'b#SnzuUUVNbG>m-x%{{4XQ%}Rh%ELfSQc-|p4c=P!SLaIDX$(bO*7Qhp?+$!IV3AgJnE}!GWi?V)bq^^oBNM5Y_1KBJ6ai9=dum-jpeMywjmQ6rynW#vuHTo'
    '_l$0#eU-v39Na?Yg<gE~$T=+jW3Q}71d1=b@(%qqj{|_DNtkX~{V7^`3)8kieBOUbZp4HY1wR9q`)ryoUcqjK=T6E*M;W?tro;esvy8p_j<MG*;97b2%dNco'
    'UvK5z-`L8FcHa88`yW>K@i2OJ{_DkyvkT0EL-H10g14jPE&J9f*V^0BkOc~I2hBi48IjLExpSctE&^>~jTh79yBm;8b{c<0q%JIi&`p&b4*0x(ca<Sl0E;xY'
    'qw#yveuGGa6;2`*j31GL1*?<b0crxBqw^#Bl}&)&!$Y9TIfV|OU^C?o!S;)u5YzmG9<U&qU~TzSdAW|R#wdnS58*7#rsL7zo(3lM;g`r~Mz_;BA@xV7!AIXh'
    'XtjTbwcQYVhTg}Ey9~NXQD!Yx<Lb}R=NkquoxmQT82B;6I$8e193og9^_3fg56Ey8^?BStfJU$~iyMrWh)@t7!^}*hyFU3%qK6`y(3Xp79j8RC#gAygr(XSb'
    '*pqec{djTys`oSeND!L^mPTfs&?4@!S84;in@)#0wu730zsSt#)CEc-8j<~vJ>F5pM<gXe*PN(||78Qm^*qZuYJIUbI1`*=X<=5a&(jsdxW?~c9i}pkPyxG='
    '4(p;4lGqGfep*;H<+6vNE;brs(^GVE&M1-&i?Hv$gzk&e(>Fd>)@;9cd-e)l%Bx$(h_sbNTZj&Y{~|0D{YHz@R_uJMR|?}HTL16=)3e^4K6`fdhAPHj7ofX{'
    'C&~Z9?_K##nnwGx7tdc}V2z0l`n-i}hCO%<H0Wpi<IVZ6{KpyGC)CF?{ue{Xw!XMEDi3<A4eeS_cKiWsKiIqIwM5bAk$Rx+NBzLM*0dSy<6%#|#yx@hLO;~@'
    'Qxe@nWAH|p7kIG1CtS=S#MR479#yv+JyBsWi%(HK`V>dC2;S0I?YH=H@yWApQc<2Kr>1)-d@nWeeA=(^E$3wjjSs_?t9Tw0+PeuUO10S`A^s>q5~v2gwYBv-'
    '%t;+y)2SCACsNJB1wR~T_VFgaX}a=Jm|Xzz%IOVApVtdM!`o1!mM^rMDR!o7Ll(;;%;%-}IB$n_3VJbv+Z%AF#<&w283mx&i0ZV8GXx<bKkMk2WMzT^bTc~O'
    '|M<kGDn4L~_4iwBTi|UDt5J(6t(BCaduB_S9}0+OP#dRq;Yol#kTU~!gOj5O>a)}z!sc_}o;RAb;KcEE#^|llq*^2eNo1+;`<+N7tb{$sfwj0TRoY5<*wkiw'
    'JX{#hw(7h&Cy73weNI%NtC6noMT{XyxSn;|wLC>UlEBXQ(Q0ffca&<tzAgN{r4~s93F|dK+3LC?GKR|SH#P2M^w+4h1M3%}vc+9%YX|U-OSz7xPb15YF77y6'
    'Pyja4cND$nD9119RhQ%X+!vGrhhC|TEV%|@DMBXqV3r87ZSZGPm8_7vL<C_=qc4U`->U~r^dk*^cq!I#X++05!l8pNXhq19xYc$21hmBmPpV~ZQ^yrS(`xEX'
    'A*G=lSe?Gw*auakVkUrQx2(5Yo>u`j&UC=oB7+2jd&8OVER(hKol8XgmTD=U5=DNVL{&F*AI^vs)vVEqG9o^>>7L+@twqYRNLz+>qTW8rDsYa`wie0HJCQ(l'
    ')HP%jbJpy0Ldr#CyC}=0#i<YG*_{f<gg+@9vlc0oR-wqDvHR3r^*<q^rD?Yz_G-9>Z!<?hLO<Y%2brp`M^CM+(FHo#YZob1Idc)k(Ay$N*RA(~TZW|~=;iwk'
    '(Vma7h{(}L@hIem?A&^ky0yR*s#qGR;Uu!N{Si`GDv8c;ma%gMJ&Km$!w`1dPmdr-OeQdMD(MAP9q@e&qeU=>kv@`d31o#>8hoUUJ7G_cEFdh0(4h`j3fwAX'
    'UWMP-zK@tx;8riU96l9DG925cXLnHazfNsmN(<e9nE);wm3>MRNPm_~VN_*o`a>}x1X+s|h>P67#chBmB*1JizYv)2vKhVXuAa{FrP8L;Xu{y47_C?CaI2{R'
    'd(|NUR8NdWHfkUzGYO#2s-DXOJM*2QBnF7qgP2`;4N8!UNHk9LjTq4N?Um>!a#NZ95ZY{1gqtO&CK;yH50OySMKz6s(C%AYOi^HKm#~wix)!BamoCVGxex=Z'
    'luzeyQB=*;%Yr!^=KGJGs4mf81F@^V|41Wj#27>lKbqYDyr%b!T2f#cqt?bGK%3Fih;4z>5GbDk7Q}P1g$Bkgdc?tEcuLz+q)A1vGcZig_@^QGq)pof7{E!9'
    'VwbJ1aHrN2Z|Ay8z0Cnlx_n$(aD+b33lu3!%4)Ns;3vZ58r;Rs2K8R@Y$a-6_~@{!C@9HAOhG4pFpt@Y1Ve#;mS{>{oq`|3|0oDS!3OmN3vIA45=2sb=LjD;'
    '9!slxCCS@-<Uf>(kZt3-92vo_PjSpdg{d?gw&s@tVjO{cbk?nmQd>Vt6Qd**?z7y0%Eyf?2~N*L7N%&uiAh%96ADcYmT<T})@#Mq<bf4#caP);6!qRH9gTef'
    '&ti)nZ~d7%dva7~s5@fy=F<go!>~C0Au6>AD#$3$xkPj|oxVqel3Yl>(i6WG)<43KH>fd}@23-^;wNW=XmCFmqgGlfBmm?HWPTJNhW*j_K4HZ;VuLSGpNsL_'
    'tvc!@b5YOV^=D2DD$6Qp9}wgTJbbVe+fj5%767a~6W}Zv@jarB=g|&3aH-z36B^g|%?9exF^)VNI_+Y01W815fJs5@*<p=4jITe>iCd>h?p>U|eQ_RrqLSPP'
    'F35|)U@o%^SK(Uh8q5nQoj?BjJ`-a>bajvB16H78jW_T|Mhin~=-;UU)TNK1-`D;C(A92+t1}vBMs0pG#mN|xUL3d%tjBbptjP+-fd}yCD7@|2N~6|x!+!kZ'
    'i;FjJ5h4j?N#_k3E#(D@xMdwrqaEk7AI{HT>Be@pcS!)Ih()sJ5UpW#Kf+Te*E)D}h4!h1eOBJhr+1TL-MV4yZ_gT`tKO!))5FDK5-Pt5fYp0grr@TxkJ5sL'
    'l~S8=exfKT=uQ6BijuG4bAu`ZOD9LkOtxYN@(EXEMzO9;HHV{28=+9f!7YJQYbS}WmJ93H6NN-KN{_tlIMu6{WJDAK3Z?38CS-W-KaTQ|-htM|71Es*)teUM'
    '-a`owCa&jd(6o}f=jhBlOw8UWiB>{OVC`{;g&&}n^K$F=)3;|ATiuPB_8#tI*6U%_m%UN9$Ymq1!K=m!rru2HR6*=+Z{8MhR6KmC?y@%nHlO}!bc-p|EXe=f'
    'B8eFBAE|jy_7WybgYAcs1XF@7t-(=6tmJ6GI@b?lDlUC5l%`8exMdcBPNGI|gt96yVYu2`Kc6BZ&)cm4EN4j4EpUf69RuEoi4%~>!7^ikwNOfCz%40~xbRVQ'
    'MtX>SA=FB_d~e|$C9AnbL|sN(i_lSuQbiVDYS&I(jib#~(l?R$)E6q%0&!JO8C5?ilv3>-9%?-#T*P<;xn7VDLl=&NXA%|5$i+b^dZ0GaAeLNfnqW~$+#sPV'
    '^O*P0vE7uuHZ`Uw&;4;(Qx1`OCbSRLz?3o(cqL%Q$g2QJUDhAmbSQpSU!j@>nM|Yc6gJtMF3#M73<2I`Iddk&y~FEPN3Fz1<mQA%X-ZbKj{3ochB1}!C)C&6'
    'wWC-+kl7bC&D0ZKaH;<3M!Nv^<ZkRamSe4OFty?!BvJ<=_ee8mIrfnuoto;FClJ6b*YYW@2<OTdI9zFh{q*T+iQcRFwVMoj>11}%_F5<wI68D{>`_@vQeL1I'
    '_)w7x=N#9GUNnm#c{+NKCmjRBXlCSVdshB)?%2@18W@AxGGs%xr>*3!AWfDYdZ2(^N8OQvi@Syde`c5HUU=x8LJV+0+P2a2M`Cj!UZVuh4wyMBmz7-SWWl)f'
    'xQT*|)jMd#DKBaQowJLv;?^nzIyhZB;oojHwM@ZNs-26!UP+yV)N`e3>%`IAS?snN9WzcuPCzJeZk{(D_kGj<h`Gl!Xg_(x3ENBzxA-3tn(*C3$?Ayux$Q-u'
    'q20vI1|#_vA~zjOfwWllWaBZbl@)736TF&W7j}-QPDAvECJXy|qT5<~udHNl@WKe+7Xf9i`II|RSDo18;&3#yM6RR|F*vsF%xqzerRqq~|EbDc>fN`~<x+KD'
    't;%)SaHYw8oYG-qU9P=MU!%&^ijA+(<OWIMSL<=@TK|1&+@H@bo_By_8s(YoegVX--fTqgvJ4MaE*PrF^<V}N;}JdY-;pL$sc}yUX?ci#yYS%{b)2mzd-pCE'
    'H)3*;?nmG6Hb~)k#F|qiy3_!%^U)3n1k<tc_iZ!6vii2w;E&OH7`g+m$%~uIw%oGKy@t_jY8^9PIdFp$Mdu-ApJ2tt_rOoR&tO0~p};bRdL97-KN=4cLL-iV'
    'smHnqJv|ZiC=LNP=6H;_XD0JbqEs=gd#1ZdX<hSKHXtwbg>t-RuV9`zg;lg#O}!mOzr#$44!j@T_vfT~1=5O8)KgN+(kO{|8;^JXU^e>aKl>n?;;X?t>)*oP'
    '`R#PNxEYbMeU=~5BD{OYzo;|RRhl$t{jEr3c%9y4^C9$&qkjc)oLoH3)k=NyZddU~zsF3S?-UNSwG)lAw|zgu+U4v`k3r42l28yc*5z6!{impy@woI}y?EV2'
    'r)gBo!bUcn1#VkW&EpKC$jYlu|KbjJD?tzJLM607WtHIZv+96b`s}BldT)L{|K$xM)*Bro9Vq;+gIYp{!$Q3@@KE>B52t@SyZAc@5I<b}`uf?=y*Iy{zb&b^'
    '_w4+4g`|(it)$B0$aJ^bs!z`6V*+P3UHaw4KmKtFJMhJ`v);3dv(s1b_nTMe=Wl<0amIHy)h=QuU1kKj1h<)XVTZ2bPx5U4Vm`7w#HkKfe~ufsC&w|}f@<i&'
    'JiD8Z78LWu4>*fF#c}ILVQo6S8{FVQb^zPy42j@}Q5>iccM+nux(`vG!@=ySN(lpwwB1|0wm2Qu;%+eqNk!-z!&y{KJuG?$_7+l(ErVLUrK>4Q-v#9cuZ?hu'
    '{uzpk_qHsnsOI4`ga%2wg*t}=)q6%iQ9FkpeAVFT04UNaWxbJ@?Y@3KB<vzEANVFTAGoU>2Ds?Qj9cze<{JqGO;;E?iZT|T6?m^WQl)#+j>u48h*DUm$Yr9q'
    '(A?9wua?#+B>pn~8m=heu5ASnw*Bmdm%90|h)evZ452HYg#M8&a={ki0GZVy8N$ZebwUqS7=yaz)8g#8q3ry0wG)`SRny2PhnMpGf0F5p*T=#VcQj`1&KL;7'
    'j`&Ia@av10&*9v`(e+&xsfa28oqzi)kfTkOOA+(}%dS0@2G%yDc7)O(+7IqP$~7gLg@O2M$+j%?l2kIXD39(PKSU7ARG-6gebRbeQsFQa0zRZYSJSIMlkp@G'
    'sw7;<2UmYwrj7ubDvCs<skUrhi=J)sTJ(6=F%vFUFYY$Y!MsO%Y^|zZOmFNKPT$OX>-}Io*sI{=O#cm9FWrd^Lr@+Q%fX+}A_W3DN`g2zD3`Pn80^yd8pW89'
    'xd-aS%wgF`H71SNyI2Vr{%kR{Vvizot6t2Bu1M5CH7D;13qz@|>k{{EADW*_+lC%JrV^c8347?zVo*nC_H#f@r$2V`F|Q_JhCyZ`wkr3s&Cvg6s^YM3-%JsQ'
    'm3^%m&YEzgg!?9v%cd$hYq1`wkh58tH9EJz?)pl7n^oh#PuoUWn(-PHQ`!jg7HM@6szvUnOP~*I0yhRXtzY|{qpHx!j?k@#T1iEr^GXNhR(sV4;$uM*VE(sk'
    'o+-T(sl*s|fP8{Tb4Gre)XH@q-;iJ1_q)3h<&e9Nnmbq{`Z=OIAv|d9lfva3(E-F!69a;^^Cm?%jdHQ|!-Yr=k{u`=@~+G%LX1>nI~@PYu26bZL-8NY*%33k'
    '8%>7OI~>5EKf_O>J@npGzydfDtc)i;w`YfFDSUB-i3k=`?hbZ~{ZHr0-oqWkV^8+Izevm)Jw}>dRpWpe(hm{nQzr#9osZ4mIO$lM_+lNIC87FgP5SQ;sZW$<'
    '8Wfi;P*L=w84J88k5Hv3L~|9@r3C`Ux!@hBQ4=Wsx{o-liH0#?&H`OkX{>{V>;YQ*y~Mb#+8Yfwjb3Bz4NBSa{yeu&JX9e4v#!ZFQz%PQYzm$JM7i~<&BS`>'
    '_=WE9#Y8V$EfFQGM~v4IA^6a+%M?KP&X&f%!jY1*bF)v4*Ijk{V0dw(u|{%S$0+{)L9?s;IUmYKuLxSE!U4uQws>zVSl#7Itt=GOL^uxUFZP)v1?xiy!pa<r'
    'g(zA(Jb0&=Z_z?efXY69DaPh43+^e82Tv$TWaudubhd=85^oQg@5^OZ;vgpy{I_)d4b=^9)`ejT*ww<MfHwidkI$&?W>RNMoQ8Aw4o1bUuxkZd163k{$`r9^'
    'Inbe7e;T=NtM}bYFZdJt;>hj{hGV36mD6|YJzUHpy|YJ=_g;KjIXc;p^7SG*DsS1ZRp&Hzyk8OVPC`!|`j4Ahw=Q=!ClJ}%s8J_n@fIcj7%cJF_LdW=ZVPii'
    'lhZK4tGizqE&x7&zm%(Plf^U_x*^;P@>ogL{<B?^c$;B^)yKq`i(`t(C&G&A@G)`!S9ebe^}`3qrG6jFtW<F;(!#4#vuSj)3A4Sl4s+La?i=9&mSWUy-4+{E'
    'la#NXdlIh>)>V>;#Ts00*-U{Wn*8U4_Lhj=G>mT|dIyruDaOVZWxe@RV(dEBsvwG5o&O5o5XGhWo*|ogg%tO}*Gi~XjsHFg_57E!*DqfG)FH=={H9J2ySSY7'
    'hKfO%_lKF1N6#3LjX)HLub2`X9p-h@BGjCcAz{cTexdo`Mko5=*S|;2c0&KQVc}8v1b;-PP_x4iRVfUzs!l+bs_n)W=o;+r<s@g<k4F8F+ov$Q|MUGGM$=GM'
    'xqOU*Fs2+B-7arYMx-{{tysH<n7*P!ne%rf_YmTpK+zE!g(D@Gg{AU0L6QeTD)kE`Hq5Thg+yQ<E^lWtDI+_sag1(=Rk$CvX^=Z@G=1Z+TaD-`R>wbDNH%${'
    'Q~{99W0VjxX610kq9u6>e80cTa`=(LF03~N%}`Ven5#+I|7Z@c`=fEfA%WQ(eRwGS?KLV4usjR;d9+(UP=cn$Q@p20M^zhE1bvu-q;*hlH6w}Wv;yARu%7i+'
    '<Nfw_eQ)=DtdScr_;WxJ?h9T-+9GOe?CLdZL{(;7c`uNRO%5b1=JQO%=wpEBe{ijS-%J|24UySpqSPWG+WlUFId|sS0EaNt>&B8f<058@{>K(f{Hy=<ilbET'
    'anaCmNJII-z8VWHA)leA9}l0>i5T5(&+cQ56Zn0L!$Vm*cK4m?6+Zs0eem?R_8}iFgkXj9|EI{%a_oC=-k$x^AV|M5AOBVZf&H{aM?G#5&YxA&+tXjpsG`!E'
    'nr*77<ZV0L4m`$b3@{+oK&Mu=z+o1)+%BvBV9{Nhwt-%)yy`cQBZ~t1zXWFMYeFEIq`;@s&AgPAWz}03TD{mo!%$xDM(QQ?LUl^a4wg!y5WqF{h!}8hM^gT*'
    'ZrN0z=xn*3DGGnr&oxW9oB_?t`nN|+TSz-M){;7bgqBUjRILv6uDdbwXITcT#ntf-Z`ZLS2s9v}eqiTT@`S3MZ^9Nj44Yf?SMY4s34J)*R>p~~VYBT2`!iUs'
    'i_>Rko#<MF8IQ9%hc+=xHr(N(f1>V}75K!5;O10Wamk?)HserTqQ3}sE^1>DNDWySyh~xT{GYvsU{qqz`FOd|q5bT9idF#B`odaAz?6`Mp#NT+Dvb{*^%Jg2'
    '!C}q~@-ek0j-j(YWg3()tz5ijNt4AU2lC_WL(`u~oxhw@E>3uKLyB;83dFQQ*<6aKnYe=E!#DFH!lL!Xw2uF>i9p#{9mL{EhM2v5;8QS%Cp2-_zb7Q+I%jEP'
    'IN-sQ*jddN2+T3_ZpaPc0iO2<F8j-j2U=86A2(ZGjYk8Rg0ueMh6dy;TlNXH1=@?XPi7eAi>U~i=`Lqo3ncEog1_tLH~y?q?|bNg&2RCSd@D5yZ_>X)9Axan'
    '_e~6NoX*AmBVCxFb1^WG3(EE*O~mM0EMDF;H#8Bv*v7k;K_KoFdNz3*v#Fb=j8@bbmnadQ1C>l$S9F+tdJij&sfVuV+u1z(IGQeV+=|SX^8O&T36((PC3{~{'
    'h5dQvOgWv6C_0~HdI#~26t`*_O-C<;Dh0CjxPLpVj!{{VlgBD<c$k$M9opWj(~F;8yiWMX^RpjMe|`BjQLp|hmI_JXw_rGp@#uOXr-@DnbZ@^^r(Hs6uOxG9'
    'b=F^?kGDQpG)VP@O&zW{K6aj=J8i~XXExUiHSnLUju`$%?4~V)gK6Js$b^cx)|8&Wh4T(CXuS8>QE!JOq*o&narF$3`@<ormElGl>x{a_hBR|15n*s6nW+z^'
    'x4f(1DCI<gR4DThi1rQkjWG|VV|+9i<;Z|U(W%86?>*h&(F#B}!J+5bg3N9tyY08@`%$&lZXCn}LKz)2qFWk4^bW+X{K#Ro)%>(uPn#{SSx5|5wo~83%61R%'
    'Xgp`KBwP0iTFvI2XlI8$Me2leizJDh@bO=f3pH9iwAV*FUi}J|4LN&}J@A9Q-FkDEXL08MtE~1Z$?yUVkUKCMHpwogSYvai-rCb6ArUki^p_a6q1SrWmqDr{'
    'L9p;}s)QOYNiw&{p`nG>oF4Lq;pdU8GjKOXTGv4iWo`&sm}Fy|kL5%-C9!Fah8#FInPP-Vb+@(M`YXs#wN|o!xX;Vd+&|z2i9UjG+1fsk0*9?bl=o;sh%HnG'
    'YbLR<molO^NHIuOJ*YSAeSg)FqhU^qScwT_BiF)Y^RUIL<b&9jQCkNG{1}>NvW3>)IxQ9tQi+E8Wd6~cxA%Iong4)MEfB5)rXYMwwc0^qCj=LsauQ&;Glmn8'
    'ZeZN!bkZb$AJm&oi-g{0b?hXPJ^{7Y!$r#vISQydd^DF^TtXWAhDgF@z*Z!=0a|QtN5di4NzJ;M6i@@A(UK@HHj(`0jCRR9Be;EFJmkO;am&><RSQXaC7foO'
    'j}9z#9R&MYb7wzBNw40*A5H7;MtsDM!_L8_gM@VwO;G1a$bt}w5rt^$I1|{m1R%i1`MV4z2o7-TpuPjm?C$QxuotmLd9u^kgI=@_>uvba+HYZ(n)N0TghMQ='
    'f9@P2efTAt*Acc(oj_an!3a>9u$=mg%8pWc3~gR7Y+2f^tpn1cwD{oASsP+X@<D%WaIW-jrG4lSRc`H1Q6<=yAp#@qn5S?l;*$gW3ErTRTtGei>GT&9HKI(K'
    'eZJhuoS9Ey!dR8#@Ck|yz|Bm_AT&#1D*ye(>*o~E(r%c_`5K&FD|V$nr`wlo*iO_@pA|KVGvq_3sy2xhbdc*7=kO-+)=j=Z$ri*V)=$PD`3*3jKv()%5cegz'
    'qXVtTrz|7K=%8$ZBJjPc)AT_VRdreMA%zOvE@Smp{0Elizz$uR7lY9$&o^QEd-k^X?DR*jPR*IF&<)`zsZW>w@$}-=*~J^&QGYw*;rN~)Wy^teNO%ygqZKVg'
    '%j)`p2$xPtMjHw7g!BjUGG+cCnpLk-^a#5tS~(PcC6Nr{*C;$CQf5_6<tgXO01o&Z?+{9C!rT83tmzM(+{L6%pvX+_@;2(P-)HxE)!C@Vy;dm<{u=H078?qi'
    ';VyCHjE`S{xU3@No9#-vA}pRnRo{B3kX{L?8ov(P>{SsQM~Ru9WFJQ9t)b7k=$fcfGCegV>90S^R&barT69}#I!YAI#AC0vPz>=G<`_rDF!h%Gt!BPik7Ls('
    'phdj45rHTo!k_1>_XpPbhgorSUvt9*EZ+@D{~_4XZd-A|sY5)Oy)F@0y6ciaSTm1-xHTTk<ivdvH41C2HCztZyQ_fo4fZex$~)gn7BO8e+*P9UDh5c>_nLqy'
    'n9>X8e<_<N-3}<^Xp+y~?uuc*VfBmHctDzj(>W(AhFKiEq7-62{HZjW>$J*}EdC>o7XQ^=y5DIW@S?`~KTy^D*i;TSX1?d^u3xFS6pH84TbVSDtxTLbRH{Y_'
    'O)!tGl*B?19IEN3AjS_Jw|fl`ew-G-;))&(6u)e#dW6c<rDki8ivHNdNEM@4Qm1v-t9(kRT&=ae@vb~r4RhHQ@#xj?(R(y7_{Q4itayu+WOLysFh)9;n~+Xb'
    '4-OT{jqT4Qg3gK$j-B$d^@X{dM^z;$;Y|z^&Oa~fK+29Ii(y^wI)rB*>4e};f2x`X3Ae|oa_rF-7K8|mUJ9kSry~EMaTM6MZx%;^m4)LdfTN?iguh+c0$vcs'
    '?NC#jhg(?FuKZLsW&Kt}RJewXz&&IZDYrL*QAy%eZOKy!Z6#0aO6<*M?s1-w*xO%7)_Onx!<yEWOr!K<Gbb6Bn3!oQ5EH8-WPwrp(89rY3`*9Hf2cL7Bpyx0'
    'P22Hks#<%>kP}ZGPu2|#rA5@QhjC3SZXxwQwKs&*Ggi?g(##(WoO;KG(?-l@1Lsl5*$>KG;(Od1et9>WfZ=cK)5(s*)@9aVQOcnn!JECr)Q>!xT)L~PQa3XS'
    'n|Mifu>a+C(oNQhKI661vF1x(Yi7Rmqf$=cOL;rYk963R+39*2EJXa}+nzUPp<Y||>kWO?tcL!5zG~QsU;e8@gt$%#Vf&5>h>|9=8yH)vP|8*@DtODI1$2=O'
    'Z47$J>M8&n#?&>vzP2*C8iuU{9Km>c7rkiEYsPKiaH5Z-J4JnDB1SkU#6eK>jp)<as)V{NNmWXH$7_+-;zrcbM)^t_#5-nV5)lpys$Nm_5>(UG6ya4zLwG|r'
    'I_-IeE!FGFIH6&k)ExE4b7=hD^xlc)%6V$9v&G<sdVQCPdRbe5lv#lR=XI7^rD0~Zn=D2)L0ELOf6V&#UUq<2SwCN5Y?ZC}wG0t0Wr)ZfTMny!(KtncRy6Bm'
    'a3OOVFELyx3jB#@jn<pOuFzPDxdkjQx9^*c{d%+2MwKtZOF_fDz^JsxTE9O$s6!cikKj`YEAgS=VZGTtq{poWJidj#OyKWki=XX^->XDze81D?DjE&#=g6yo'
    '&8bi@*d)2p578WBDg<)J`M!N1H7gvp==<Frdeq)ccwuh)6vNlrrN`J?#CrOEm;1Eah|S5sC@~5lVnC{evvEmJswR$(0437JETE>(wMdk`V#yKTJTcKMlz&6O'
    'z90w1wro^gOG_+pP)j(I%fXG6vVatN+UzT~B9QDScogm^4v|k7*;x=;{R$0C<FO$NXCG0w4ri(Q@$hLo?kJl^$a=^-uDuJ3jh2E|Lrjl52VxIl%cJcgs*IVa'
    '@I&CPXs1bb%RT&<4fVwq(0aQ|)`*>*!}v(f0<S6^2R6v<9X`b^TCKH{-GjYYx4E~cpSSmR;Cu1rkgwYEww1Ktt=(Dus+k-dwBSR>7B|Dat}TF36>XEal?KBr'
    '&Ps991V+8NS8osnM@P|Sqx}^AyVHdKw%P|z?}kk=HvbuRiC_M!_rvKM((sCQxD(+4Q5xb7ES=F3cOpCzwx+lf!RWR29=~k_Z+X(BccR^fQd7f+R2S*Y;X5P&'
    'c9;dcZ(#mC(@$*~!PE~TC(J&<j-O#{tx`tw!~8w%4JC`<6AAW~pO$daGfliaJ4I-$XQGKA$-6hEgaE##4C=raRVZ?8For$?pPU#*I#G%5nBhYsb1z?Nji&~+'
    '!q2w(mq4B~vxCbrGO+9JniZy*^baP9mr^^pUtNwY0Z7m47e~z{tq0^XJ>Ses$-I_%_<J+^xVaML-KT|$1=Z1J%o6ry*?cq|l6~w6YJ#t~2iNa_am1?>Uvlh|'
    '86ebj5)q2_>9e=wB1j57c>GttN(sy<vjqfHdDOmW@aP|<J|n~o75oQ{byZ*N^vN7~ZDPn&Srtg;B)%*LL29{+TU#S{Jx1md=Tu+ZQt^RGCb9#cEV-y4iHRI5'
    'Oce}-+Sx#S+^F+W^Gi{885n_OTv6xF`at#0SUw-2*fS{jdcQlhBzg)-k68q}S21FNEPb$p%&vzfm}*hM0-jMYevi<$u!dfL$l69N`*R!6fy8d3|Eb4u4XCKQ'
    '&F1g2ltP1jmERT2+<QCup$uIqYg4S*yjMs5atr<gvRIyLC2tyh>F1wxYFk0F_;M(Orv+N*gnBnzW<9ORntWQgYDXY;zT&ZXpNNLnx=8*7v1a~+Xf58u@62+S'
    'WPcXcE2CCP@TF_GI<)MwiVy7QIBDQ6I6_cTrwTp6Utdb)dcXO9uVnwz>D#l8kvLISXGaz?ZNlRxmO$_%s^X)a2753f17C-7cm4TL3o)K^7E9ZB>C{~x500NI'
    '2oF*nQ;F#6p1lLJTaZq83$Qr+j#6AJ_Z#Ys7L<<IeT4-nESUQqYRth;J5isl;}UOX)Cwe3vC4t887Nt?q_1#13UU-VM!KTZFuOu`*5NyLV$@=jo?Eu-lR*>R'
    'Hd%0zsUzWvDiy*pBGC$c#L!D|1P5}m@P(%iI?hHHz!$wbV?l~zp8h;uANS9{hTH#oexLdp;`nis1bBXV%*$btXX;l0exI5!8RhJ=V6pqw)5k<X;oXY<X~(I;'
    'g4;XXTZd`63Dm7<>cSF&Ug-zQ2>LrmO0d?#l@p{7<+p%6#m?+)Vv#RT0rPOPIU$<<Q&hFetg_PLpHa?l<k<EOceMiu856j&?T`KOGJ_j{a7v^BV$gdR?fu@*'
    '=NB*jasK*ENh?XziY?~?Y)!Vv>dj%pzN|xhNunp~(OpmqBWM>3bWnFo!O;$gn|47%82i&ef5Pr#SWFP9E`Y=S^}^kKSdir0(d1)w#JCCrB^w~bA8q0_>F-!j'
    'wg5rm)zh`cw1w5hUbtUC=tywB3WB*Ss}#fgWWr2zp9;pbqx_T^L+aJZBvjpnoJyt3!Jw@1>gql$vn4rct7C$mL8Hk#;HA}eX5Hm9mzAI|f;4{P&fwjO8&<VR'
    'TrgaZcs`vhLP%?=FlQ3_2Ev=7lJLmVvH0TCdOwi<$Np&Czak_UONuQT#5{Zt@|@7$LNDy3GAEeEbZyfXFO*yEY|7WLX9yMir3n?&BatR80>z;>JUKSa$|ghC'
    'eyfBW7wrg@FNtXv9pJnHxQY%{i<cD<(U)*6ww|Jlg4tz)6wLF!E9^;=zf0j3vrMUv7xpFul;nx8UK`F4FG((E8Y)xEBxNW~fyRx(2LWFT%9Qo(tU|5X2qM;3'
    'PSDY~1+H}=TTt(HZDUuRt}_{+PN`jyXn>v2@lo?l^#^9iJ{Zc!(W;ui3t8{Yfvl%etk9}+aMv#n>vwQjK5&k?B>KP*yrz!@rOuj^g4Ub|6A8*G4YU;KFUdEl'
    'tbs*ysRB)F{V%lk1%DK@EuM?e1yJudr!S4U9R)m(Cuf1((bKH`md6y#SQiiqSVIsH2fU^OhJA-?{g)#F6^CN$XC5Hmtkum}<NGGsnegoYOEolB7dF+=r0_pc'
    'JPa1|1)lTm*?k1t;Fq3y&}+B%8oO<K7yJpz9gzH=y}fvQ`oqh!4*OKs3Bve#G!TysHee5sQlYCde)j8R$nd5F2-9jr|0B3Sy9%WtG2z;*`M`;<w<2rFBlh5n'
    'D0{2QAShT7CWPvGM3}6~D*ypjf%LqeaO%JOroI?q_I7L~$Jl4WLn07}cNFc&VRl&B9t~@dEjSrcYAM_p1^^n|WW>?Ieg{5O49Ce{W5?jqkog$T8^$SLXW3Yi'
    'dyk^(;r`)v19Qk89LDT(l}G#agGg|bu#Lz7>Cn$6*Yj!$mCWluQRb;?yUo=cHl!LAi6t}dRHS}4zxh^q_O?fR#DqS1Bdk{U6YR$-d>42Ng_<ECncXrRnW%cO'
    'NxcW<^{R^9sjODptLtqwsN!}>#rRr9Dm_za4dE{@K54M%U61Ch*dBxtY6pzAcK@h^F_zn`ElBXm@&II;0?t^P*_PbUfMp`vf?9F9d8?!yta3tTs@!B<PNKH)'
    'KQ8ecyj0LJzKmj;^qqd6Svme>5*>PuUs-uvs1h$!10JoG&{e!t4x}3-^J-4e1_J8BJS}2!(9@}MRVUyZoN$UCa$58wsJ=0>4|&X+&iJjdSDl+V6pL@h>X~Hg'
    'Hm~QV4wc5^$AIPVpO+nzH=!I7@!#zz|Lhwj{d~4M+vi%G{{l1cSganK#ym3hrh6X03SIHpLxB}7b_uWHYjoFC?2>u_Gj!12`4_ND=f9m@{P^<x_ozA}vcZ6a'
    ';(7HO^x&eo1J}{%%`Lq90TqeSIc1+boncDEdTYDEECal_!GP&jn?u1lnLq{o1K&*rn?msan~g@Dz+zE@cqAoUAe?IfuFpYU!g%`o3}IH@pdYU7QHd4Us4#>^'
    's6LR2@1{#~)a0z1oY;}^gr>K%akj`%MYpIA`{)%&Rej6`=qqO<P8duC^l@bmRWx2v`ipOGX6l{)=3Twhk3Dk3!K)Yk)?y3%9lD0$F}cm<AxjHhq3A9|py+fm'
    'U!J~xeRk1%{pPaL8zAHuD-|nUx&<qA=T^Fx^n+<YrHdeG^qcFcD56uMSFf;?QsGOWf`UrL*Q-}ZYN>cyDS-`fopV;?`zleTRtO@x;)mZ-<(C6-x8a|zMqPVJ'
    'SsLpZ>vof9LSeo96<uLf23v>bWnwNXl#RY3nRBp8YaD&tYHL*Wx*`i!8K&FE@LoM`$GlK<ODhT5b9M$1UD|p*UNqPr&R$CNa1sL6RBTiQuLI~YCm%@Y|JnQ4'
    'BC}3S?p8*5rrJ-UD>Y(8na5)?2=&d>k~RRJUD?lc!T>~0@5dnF;U8DAcVr5jYf<}P#zL{)-vOuEUd<zgvLIHNf2jCb5J_*ysRvo79Wg{s)SDmf_pX*has$Ku'
    '6%!N&n(jHLJWLZT>rR3n^vHk<t#KE7^u}yKq_}u)rF}KT(Yw*4KL&1dn&+y5VKyEi&QDb;*P8@^uU%FXKU)W6ty1-BvjOZNOnZfSJIQ#Ut%y2N!f5P8tzY%u'
    '5#t*?P=T0zIp6S^I^5oonYdPrNgN+hn1m>CCyD7eyfK5Qr&O${EQRBXF9Lc;9L_e}H^k?%Ht|VRonTZad=TryL?}Q^E{~!s28}dPIJON4YjkFvKh>&A^}ttG'
    'Hj6eR3D~9sB73__SHl2j7I(2%`$-@KYPHXscRXs6#Efetve#JaGzT|5O$|#cx~9v^3d#+YgeZE~q3wDSWCL`)c;SZ}8r1_!B)R5u(<>YrsXTOOWHvNqG{=u>'
    'E6gMBfvRdf5nm5Ab>=8iNf8RxP!`RgTviloQnC4GuK@8YTmTO&HUw9ZIkGP7g^|FNCM~5eNSOOd#Lxnd{a7i)zAqjD^X|?M^Kg~NNg%qaO(l@?NmiHSRg>wY'
    'E{Ws`xe&d*w4>JKCc|uRz+#U+)j8?6nE#38Jq2zYlhhM7Hs=##ghb?B`lu_}j?QV|{jnW@B#FduLCCFbnKR53x|oq-axuEiFm7bAoJo+AbTQ}XFN9vI6KWO1'
    'hw0q$$ea)6*&TGR_vR(c%K!fL?9E%!ZnxU)-aPxTB%oS+`TP0B-_9=dJDv~qoul;vIRRDxo!^P&rY!=zEUUqIEbI;ipT2$ZlJh`Scaz;XsqWE#_vOEP^aTIA'
    '3;(sbk9^!4Qtp|gz~o%z)jn+f`W5c~8vktK&t})FVb)*VV3L=FQ&8kyO?V^q=DTfl%D-JM*cwz-Ws~>WeLC*nUJd&ZR@ABLPGOb!h&q7h*Xb_vvB?!u%YTk$'
    'h%b4=#hV?B5yn5+wMUv_J9*UsGP0J3*b_PaB!(pH?qEiPx|P&g;L<NdpTeFQDZOI;OCD7W?GybE`a#OpWX?-UlE*mziEP7YG3t*i0kCJK_)&6Jx<Y_DLV-E;'
    '8Oy(_^jwr7C%vR}ITiX*k#spU<DZgyay?L+uIq4A#2Q=i4~dmOho^v(`&HsJtx!_*iv5xj-wD-D8c?QTP=BZ^@#>-f1&AI3#O5;;s~Pb^eAJX|^AvLg$bs%h'
    '*GnNL(QGt$k8ZM1<+fVz{_sAbs?y$kuhkn(W=p(e`*UZrD1ibuT&m9leV6EI(lovQF&n3PBXg-oZ*rv$6}p$=_qYr)o!2T2P$l-~vE~&;B3fElE;D6KPw_-o'
    '{SEZ=X=|s}jGus%wck99>ok1^<(vjy(_K9Y+2(^Q`pl5+K_3Hdk>$<i6l*zTBNY+hEYH!_1vH;L2e&Z@49-2r>~d8wtuW4^n@ZA&d89h;;NC*UdN5wn86@^5'
    'QY_N8?fTfG-9+<lqFG>T|NP?OtP<2pD?T;3)aysBra+9Ehaf6laT2-;)hsL0t=Y}hn%XamyJYqgZH;=fn{aJ6Q{dCovpB9bLn0+ET$;8HnLajjZoGU%YfWMX'
    'xlty1&FZ|Ib-kQ*)fJ1aqhTGV)xEl^EPhhLsb5x%Bk?-&28){xrnCEP1k%PoB=54?r8#QZv6R(Nz14wL0e+j-rJJZfy1GhJm{=E=gljK6wBM#pb<d@A#R%j1'
    '8(t-fwIZg47E9eOFvxnUm{fh&Usmi}9+o+6u7db741=OS)46}?ioBwpewPNEl?@*fsAt1VL?ndNRmL6Ro+{iedP}8NmPOIJbuX!T+@D7v7pGw%nG4BsO@Lm*'
    'fw_d6Y&m%c+rMD}#L*~B3NBl|hpQ{)r$>u4aK9BC{{lA|HsM}m->HkNkc@iMxwcw_eQ1bwx5MMpyP~w9;u_$oO~|_)o+=F>N6kvBNE=d{OiV4mVQ%;Y)_?~~'
    'b}hV;Lpcnvio5>!Juz%pmr}NpyIv(xUn3FWiW5&p^%{vSrh*1wwd&ro*diCPbDb^c2wv<hF%(5@EB)K(x{D3ZtS#e5aY}s_FC$Niw`}31d#?t*RrgR&6W59_'
    'N&8I0SMkL~KTgdx1dfEe%PjtnNMCK`m(ETseCzAOA9Ir-c?sTLW{ZmEi&+*`-eyyb$<W#l&6@BlI6pPjx#LvV7f_VBRGoMhi=YQ6!)4{!`OBAQ&))Xz%g;~f'
    'm&!^PNEW}QEiHdKyE=S2g#r)^9A3I-&nw*$lEP_LD$h>wqKq|vt+_060UqVrp0%wwHAZbgUQNYV^#$sa>}E=r^A}0dLA+J}{)k{pB*6uV*MxRGo!_E+(`Yy$'
    '7o}lFu>;s{zP!F34MrT8<t{cXY@J=7LwlsPLobcM)6d_7z|-CA5_#Y<sJUHv+=~_vJOb{4cWAdPuqnZB?Xx1~H#sSokQpkeHEU3(y~$~2jAt&CN%#U+mB&`@'
    'UMOlSnxw;Y@aSb+NP3x;Z_agRqvWuuiqm!9%juBvmbFFhJL{{5UV0c+19zTX161pBxUScRGD}*Tw$#<6Rp?<wYtlX*KHZ6aJL}K@RF)mBEXzL4`jedXT%6pz'
    'DL_bfQw6)kxcm!*wI|y&VseoZ?Y=)JgETPJ+Z0&Ius)oUhYYN`QWl~`L5F7Up-xJV1sFaj(;)xNef0Q(|8K+pa}o~Nj8=An<^jBDqMeRk?suX-R(3tQUfehe'
    'IhL#@8K<1X#^7@j<5^F4HC=Khg6A^&K3dK>$%==_LwN{h%Q;4&Wl@!!37V3!3$=u!cN3fo?uqCUc*xrH&v~mC7++6n1d6w%)G(5dzABdc!9sy|3Xl}b9CmgQ'
    'QgcGrZa9-Q>oM3(hSeEZk?L-|9lcn{9$*M91_sO6t&{V!5bCc^45J2Wke7)@qfZu6+&KYOafS#=xP#46qQ$148BqYiC|@HGZ}hjk!-N?8G37Wxbgq6bV@BoZ'
    'Z)d%;moI*L!A_7Y(7@&T4uwO0?dm{5;)Uv(%^vxYk{VP$VzXoq+QEbX?z`!G2^2l+y@5Lpty02WcF00p;c(eXhc;w|!(}TR?OHM6vQ!!$QMfGpI%s_1S~*aT'
    '>J{c6zNL!Ke}}(!=<lD-&)=NEuQtWSx?-FfH5)};O{3?m=t@z_S&?koXb5gLLyqERqMa5t4!^9>Pfe+eJ=c}@M3l$`@^?`UGWI-0Y!k1MB?gO*iZ68-Y>DrI'
    'bcR%QIfoUOW_5=>h*{iY&%R1750^Fow{{Vs6jb&LmQa%bDt93TyApOZeu?7}!6@NjInf?bjVEzH2;#PHMa##1rzt;C9~O52!Fh;h%s3-2PdZWBu!rlD+K-IA'
    'kh%#6DCA6Rtw(zK`F$t)NVEDL4j;Kw+TJMdaeK<3zpPtZFXY<U!3qyk+a*&PQ|up{@c0c`xvY2u#j$)jVcP*El^o6)$Lq<~BZZvjB(w;H+<AEP%{K2&e|r|-'
    ';kCXnybE!zrhy$*WGNM5klL{5vi<V(_45kyEhbWoo-=u?Bx?1#ol+^rn&`4tkOYTzJx`_Vc}C5D5-FN(K@S<99rZt;o?aW`e7<orRUuX?n3P-EWeU|?-=56S'
    'Lq^4)IIXR2hjf&oP%sS6<O^U$^G2Ucdz9n$yae_diy2E?4k@v`TiEzrV9(0+fpB2ZmA!%(;`@z81HNnXKhz-y)HQG%z017JBE9ZZPv2Jp`7Ai&eHrrWI?&fJ'
    '@BLP#pmP{*%sNHs6@bx3o|kyg*O&{Ap%SmBnAeFoD&Tzy(NQefglMTO+E>eavO8qLQB!%&tB7Lv;s!*|yd&Hmvc(GG>fIb!S_DqTQkX6c9R!IB23DJCl}g8i'
    'Y$EZrQyB%~sOD53Go*&4Lrz;b?>aSl!wf6-jCCWq;%KQmhRGHAUOeEVQ#RI%1kpN(`a?`IF%^i`$ubu%S8Ail6c|pFXVg3b%c94O04+;&6CQEuPvlmiW?`V;'
    'k7g07Fo^qnyTUXNFUw5x^xd0hzbc+}2jln#%S^p;IMzjPGG)!bGTg(X94366^<)m6H;mcT!+8;&^{r#gk9IMFW>5azmw(~;o;=@^=dNKNs>Y@0k(z=qAuKOk'
    'b;pH|vMZZ@V&K|OZ1vThLt)uyNL`i4r+ZR|z(0+yLca4tjuAPt{2N!nZm~|Aedt(`1)QS0%Ia@9@e^+pGW-**c<Y${OFmm^+YkGul0)aA(&AeV11#GufG=BP'
    '`Bwe{X|&SaAnaPerImZZnwIE<r=cCDypKRmBsV?^Uongnaz7zMC<oBHegs&v6A6N2B5JJ0<N)b!Xn{ljM>f?Gr^7Zt!*)^6*VKqK8E&h4uhu>LtGDK2a;d>O'
    'M=O)_$Te^}-d&EdQacqc7lBD-A4A8~`K@LN)AW?rxO$dKtg1@cYOFg!uM2(Z8ZmKExK(0pg>~jWKz2j?!D=h3axVAmtSg0dyxmeuPS<-IUx?FcwT0@g!;o@O'
    '-$lU=JdBR7mfX?sl}4pjSzKi;m`y$s4$oTiEGk1I#eaIHMbsfv8n~1k%-9wOtza=UXTgqD&zt(W?gB^Fz@{YUU)!g+T0vMc6j&@ZYiz4@mA9{Sk~oVr+HdZw'
    'Wl4zylbDS^Q96U(wAy;@xOGx_;=-P!TuEIIYOR_$D(Z>3Rv0=uoP4}gztrk6X9gp#eoCVISgdH#y=|>rbrq8-PJz!BFHd@1dfRp_`-tVyZq3($HDtEz3W&x7'
    '%!xc08mMazmkP1hd}Lf(G+ykayIo;QE_!!wurOk^j&voK-P&*MQVQv)p~9GK)6t0FhgNzXh(*G2p7$qRPYKrHPATW0`?zKjOe4w$Xx@_u$`#vuRCh%cKc8Ow'
    '20T%r7PrHyvjGd(s>)Z}aaK%=Yknp@oK#zMH4oh#7GqusBnp$td{ez+F>^@Vrvh=iN6wwjb)u?UX;G6CpIGw~vaXeEam%{qo4ttY{0Y=6Xx~zotdgPvtn{k*'
    'C+3%lSg#A+(U&PpZ=r_D)dFuHs22FfQL@j*{pB!=*iO;nxZRG*dSThj7>YxuIgtXC?PP`ui0B*@0%)PXh3=B?H7O;2SdKt6!5rSeKIKmb)Lf4;G4!|+3=Xai'
    'Gop7R&dxE<{se5(-m}x*j~C~!Fk^Cqf4)7B@IdnqjUifZHMXU|^NVxLr>uYf@avC1lH@MmAW`c*Km9uj(M^8z?DWmgSfC-FXo;S+L)6mwZzOhq-g*rS|1&1s'
    '1tGnT*}Avhod2qy(1WwnH<XgM$>`r(zn}5%dQ(CzsZs8y!D_AUu)uEcS`i#$N0oo`_Vlez)=Qlf-NNUsLBE&Z^(n^^0<XePK0ek1;d8U0c|_p;<`=Q$XyRMY'
    'LthbyWoScjNpj#cU-PyIzG8kKqdUzriEb}z2XW4+Ehuq#cxW5Q;4Nyvt2w;IREeF9(|_iSdlO9fiAe+Yn*pMsRQIc_Vl4)&0G@Ae=YW~SFixq|DH?qKYF&bW'
    'KzaasF31R6)tH$HoNmN`mVw;#$JfwndPc-iMIH?@iiy0eQi(d+Ak<%Y@8I9XC#IZRMzJ^3!2ow-zawy;efDm~wk!h(#k}ecyWzqtYs_Mb+Zzo0Y`25Kr797S'
    ')JWDPm^x}QiLBre=u;Ix?_=&sdc8fG46{$wejGchF__Yiump?Ty%6}4><I=VNSjV1*Vfh+{H#-+YJ=vP=S%WvV%F}DKcJ33{$MNv&gzbWLKV{?!%J@Hk3V8@'
    'MEK(mYV8jz;W6%C8>U7>Zft;JV+n*Btp@9pmE#SP(pDr6bc;Ap{dvhg(yOS^R`_E9|LT&_lwaJicydDkhE#~rz$`E8@@&p*vn6(hmjIpfe0WN9pilwL4uXup'
    '_WFdwe8~<N3=L3@R*7Swq3BXBUZoeQYkE)N@*32(z;55-#8Vd#mKnJkp$YViiGqI3es|KNqSg6!C~&m;#tK=8fU6ubOo$Y^<PW=nEQ?Tff@SpppcmLijjC~;'
    'HtFeoFui#Laa<;!U}U_9a8Ug0UOg+xdTuv?Ys5Y3225i@8m#gpuc8(Mo2zngo`o+%B>Vqk@7=r8xUzlG|L+**J5<QXg^CIV^l)sX^0<nv#2&FNAIWJa&1KLC'
    'N)|Q(1W2;l!{7bP*Lv2f0%SRz-Y30x5>d5kz1Ljx`J41K1kq{b)~>;ZLF{6hrPy2PuC-4=xNRC`nAs^_7VkiQ6I7&Ca+^aBM)jnG<h%0mLg#(o+AgXTr?Z{E'
    '0KD7ERe(YJgRBqCW9?#u^w9!907CT?U!gbActP0xjLJst(`}3uf#UF4j2}@Rcvuu@5g*Y<hSv2YhFv}|(ZIN8diiTw`FfD!T8cN%8BD*b8>WJ@{m}908MCGO'
    '8jJI{up>?-7Vs1&1OA~GEL-rG_GGXaObW^VY%*m;RLXb6*9Zu34OCyEXxk;yo+1-?gAQQ87J>XpzsHjs0ya$>PEvO2T}`Pdi3%hX5iR_kdL+LHFH5do?2VWd'
    'QJ?>>e{p}{LgD)V^{?9oTt`E8rKMpAb|5FS``5ozpP*EY*4&uxWNEdTjl-d`L2Op=;&y-%;8f@gGP`Z;lTxvvs;&lwh>Tlz3M?1}hVwLHS|L^Dd#x))f^;iO'
    'Zq0_C2iyXU#6uY1Gdv;ogXhB9My!*~+08+WL)#s^tgD5!zR8f?@lS-BHTQ~vr`Tu0$?ba%z&D)!hcj+J#t8_kr5Z_iux`$$DU%b{x>Uk7DRg0In`jXZ6E?p1'
    '5uwDgQbPoLPDn0@Zua!~FARVF{KeDmlcS^8<`-O72pC_9zhGdxkF3bKftj*C(zB<gKY%w7+9gmN7AiD@Z$a2PmW)#qqB_t4_z!MJe2AOko76tYUX#`v-b3zd'
    'l`#sA2x<g3q8f=2hECvU@mu!o^56)Hr_3f!EUqmki{8k#@}injF@vJAthh8^IqLxzd5)-ne2Z!PI@eQAG>Xn^Vu8lj%A?Cb6%K`~w7W?HA_nRRZ^p+54KiA~'
    '%d)`|k3O7BU<)-wI$VC=a~)wu@lWIjsrQ01(KLRB+)U0{u!8!Dio4ucgP<4#E%m{R2ifS0aEuKQg|2-4B;#RNKt~A43o!xwz#PJ#C_a1<-cM=IfPpK+2j&}K'
    'dB}wk1PaE2PzwZa_yMffEYq5ahJM1@52fCKQ$M61pK~0#?rtbXNb7X8@l(_~1nQu5I`T^^bmX^6=jEz$(neB-3$LY+ylzM8$|-i_xzXyZ-h@JhqYAW+Cw=tj'
    'QS4%*1~41Lk(Ww7*YTHZeM8e-_^z>)z{SQ`S7bK3G$1-_R0L(bQKGXA@}uajwclO3>${kiC3m;J==Oo(?A{pnYUQ!0RER{4liXX2R9m&#a)D*_^~8C8vrL|M'
    '=%^x-rTJ_uWkEkSRC0Nan<b#HwPMs)y9NcSnEFnuh-##?(EEHP?=#tWa|Au!$-(L#7#L4mli86AzqmjWy0q0!uvhBasJTgMd<2<6?tViU095)T#h5bEBplqi'
    'E3A?pOYzo2(V5|ilTE8Uv~y9WY@MW1#lf=H8Fhd@hL|zJ0{ej9yc{SHR7gr!8&-^zi<&7U-K9jYNmPHtczW_QB)Qw;L2C>R+H(jhcZH@b)aXi}(iTl!EJUNu'
    'p#Wi9&ERTp!jps5ukMzOez)*JyU{7r9C_U3mCyt;jh4Z-67ck8^$~L-tVSx4BP{Ex7K{vc4vjw!-f(Jh<c1_2?(J2$oOeu&`J(izFJF2UVqmO57!K=AjjdrL'
    'TH?;cK1>8Wgn8HxU-jXpSt=FY)M%meaKbbyOGMsf;n*9aOj*LwW`gJDsw~Vk5mH;+UafSoJO8uv9Pakhw*3LWR>!$nh)ZAcKU;l*Q!ic#+>&}p*8PguO@NnM'
    'yA`dJv2e((Z9>}|C24n}LljBtZ!z1BI#Zo6<yv+));}2D7s@mkO1ZN38Pc~VTT0ChwY5n%(cA`SxSe-d5rXk8HQ-+0%qWX3It^|$U`A1HL!PFNP@@}>vGT5X'
    'C6n8aH03k=7@64Z%SB9#rp>;0O1Fq56Js?>D7G0bf&L82cvhk+r7@9D^SBGd0ZcyR{Cu==fppRCmBjZ=m`)?r!sfqmnwNwD<akUDYmS|Qm}!}>0xDKa$&B})'
    't&R`&Eyz-!7>86i;EA)m;o+H?!LT<^V4}-7FPxlWJ%!^^5C^+MPRr6(Yo+VXvY8hh(}FZ&ceqIK{A@%I_!3d}O%<FL7}3p@0T}h}6D3$cmFg-9QVrO^%WkA4'
    'Ra}XMfa_8uL9T4kV}=jIRSEIAxhkSQ1?%Qe_T0%XU{d5*)eF}(Pnwn#7J7~6rxVgP<||f0N%7|Lwj?{4lzmWq8EkLzplzMlP1gu*oj{x;zs(0V=JVJIud1R6'
    'EAqH0i8<AtRI3sqk{>cu12|K|k%}CgD|PU`a#tp_HC4Vm9ps0Hsts*)inipUoMXmMaR>CT7Avh)&QGU!FhSoPTIIsViq_d1l?idI(+Ep$k#d4g)>zyo>`ch<'
    'kzVcIQ8U|1SxzT$KwDsnt;k%|C2CvqGAg3mB!tO9KA-o<G3hJv51y@q0|Zm8q33BT$z>Zz38@cLaXXiyJr)1DIuEoi?dQ(zC8YsY;yr4BL?uI6j(Gf!#aM{$'
    'cpFHOzmF~hTgFeY6X<LbU4{-@fUsiPz@<F1?HpJ1Niq4`LGm{mMa<fVbTg8uN%Q_{s_>f9a`lpZhAD8nT9<F7;Nv^0VW;5ZN6nU#iI4yI>?_GR$1-nUC(p9g'
    'VB(~hHae^P9``x&(df%Jt4gp`vQZVouVy%rfz?$P;_!wo-hGm>sgdM6P_p^-3fEWKcIctG?tVjR!LPi|>%EarC*>9~DqpQ&@|91jplE${xn`@NU?5RdQ&n1;'
    '70H>9Kvtv`Ga?=QC0w>CFW2ki=h|r-p_AsExdN8*lv4;%{<rEp0=a&8(Ic>P*rb%xmNOLG#c`Y3fD35rPxIYAI^KeLM;~XjtI*GrSKVLPkgI+^b6&qVdP7eh'
    '*blUmcXMmg`ttdk!<Q5YU3vNZ#jkk$3^)(Tw?{{GC<&hj|2X{R7qqL=_vT}tJ%qm)@+V)TQxpD{cBv&*^U<qcj-J2zh3XDgqzW3CpbCKj0R>hSKRJ4fzx22;'
    ';tC&7L!Z?YJUe>L9_c?F{CWr#x1dF-fCq)X<gcIq^PdM)mfou>P0v)(oFDd2$G^RL@~nIEnqAS|s=Xn>&p!^1Uv*F3933B0X`cN+wa=d%cAp#{9=tT2@@84h'
    'su{!K8`wxcbH!?z0#%>9JUV*w?D=77&4KTJJ~)1Pczl8z?bkyd?5evW)~jKA=i>v*J%2LW>drDb<YFbpXF{gC*Yoc6_9N>B5dfvy%RSeA`?))T3K`#e+gBXl'
    '3}(HX8lkzd@<K^M_}qf2QFiL@q8;B>jrZ~xGr3X(+hppyDhV6|=^peRB_;sBN}^gENOP^?G}Xr;pH=9gNmmU&{QNKMJ;Rx)xE8V!HI@5}KeDah&{R(hiSSc%'
    'E$fGSDPak34LBkm?^iYZ?D}kD1l=al3}g#OzvsGTd;R{HutSU~4&N650y((FY?WIFB1n8)J`BeLvD~pdVj=a5SugBUE5WKAqL1h!MobZu7nyDmH2O7_6?;)&'
    '%nD)UNLdbEt;Bj^neeXAy#uJ*`l1b8mC8D~-uBn;Y|z1$PVmR+WPUZvT&0~(6`w?>y+!}r3WUQ1_50!kL+|u2I}=j(c>718ap>lA;OuVYShlG!-g~nirEWzW'
    'FGeqk9W<|eZOV9T?PN@`Mg2idOwg}ECXiZVyZoomaUio5L52}NFqZVm4n1st=qS$_YSf8M&v_h$)9BLK_L9I+PF{jio^9)NO5{!<Cm&nbh~6jC50vA}i}D)T'
    'pA_gta1P%aS2tK^9j-zf^Xs{SncDw4zF_*E{Ss#|-f+|zI;%maFx^stR~WJ3=oL0p!A?W>-av1$=`6d3GT4RnJi+MX==zwED6$)v60rS^kEEBQI`6{NB+)nM'
    '#$?@7RE0gs<7+YD;mB7zQ+!2w7>?FV*&a~Yb;J&PG<O~jJHF+h{_NWLh>7=BJ!-bXnhSO)BU4JA_aF-hrf4Gm1MBrXVM5B{A;uu_c|M)Y#tAv|LM1`v?(N;o'
    'XXETfIoxp8$VrGuyqhfCHMhy-5Tn5Hf)=kD`zo*`l~$n!w}zcihe!p`)2D9_51;bpAR|)Dpy5(nS?>6g?5548N1Up-L;=iW2^cQuGB2u|mH#wW^@!EnG+e6('
    'Dfd7>+D0_G+v33+M)8|+#kKSsb|6<9E~y5A?WQYL7+h3*S7s`JZLay#d^SV4a-f3clq4X8kjf?Zu}BU^x{$MpqCthS3!0-^!uc2S+t$%H4v_AU;B+<DK3y29'
    '$*8nM&t%H#(hxjVtN@0z<=A{xZgMmBdK2tDH@51kNo+=7@#<Vtyw>^|6(W6XzC|!VBX%g8O@V8zABn5-$KKi9QiR3#271;}EthMR^SWB2TvD2IIJf(9HS9+Z'
    '9_<9?e!ZA+HzUO<$+#-a8`X21o*MSUJX-+Y)w>$O1kAP{bg3}#8o<|*492aJT$*?92%Ze3>?$T!+#!qK!K>N2_?(S|)&o6ZcecnG{Eaea<y^z$8JEi`{3X5U'
    'jc;qlIIv}m!esrm@LxF~Nx`#LVq+&(*M;82`BcX1b<4GDSlM{Vyb=2imD;t*xRC2>0Tm$J9Lrqe&A&Exguj+F!Hw|SQutyxVmkIl>vnUoHz5ZgY!gOJJ#Upe'
    '=@t09nC{;LNJDT|DP-tNaT|(iM_tF5uA?QJr7)m)RoBLQ+h%sR>nW2T>e+(m+>$%dH_S;*iR@m<9$mU?E=%rHhf3Szm^)|mcV)eXoqJhcJ#E~uY0lZ&rTz2>'
    '!IBZJzkaRdTVq1pvE@*)5y%66htr7reo6B@Xk*A1J1VaMcA{)+=NKL&ZNSWtjnR6^C&n%y>svm`6|AL8?3_Hh0$znJU7A~Y_|Ronw84MbHThR%Vz4&i5GU(j'
    'cAao_aBX!-Do4JRHo2~uS__a^cG)QUD%77f_=iw?es24F=j-HqcRs8a_K5GyzLawj#he&@rd7{(;STTIWxPWY#lW=T^1UA>hK}jqY|Q^)HpXK@2%@2cFSu_e'
    '1)H^TW-jCSUf7N=^0quxv5Mltk(A4m1wFp*jjl4K9V)YFVTTh^d^8anrkKDGd9|n^x4=jcumMWOD}=d5U%2h!3WOCmsyRpLNLNikOK5MIUt{<{8MRP5E_Xzd'
    '$a<vdF8jMS;<#*QC_u~Nspe`f^*k?MU#sDQmT!QL@x+pU9nK8HuFYMuL113-ygug1l3HSi=!(-1&bYkC<E-GZjemxLeg!g8&TFpQF3yQ+8~I{5Qf2qkx6uGG'
    'chG@L%?o;W?M3g9RYE^r4A}(=!<YJLum1s6=Dit~99&7-z0x&4yJBEhvrDZ0#pO~)@Y0jNb{@scB@bzS31M0Bj$;iZ-4;P|Yu3D6gruf=Waq&xh*c)i(|GBK'
    '=)=b=4Tm}jw_)3Kj9B~|x-qb#<#oseg1lT_UZkQ~h8kPFOP7}SrKnRif2X`bI?FZ)PzT~5vG{i9j>7e+nVjIlo|;uH7qRo=-3WseBnqWS!ZT%Dhnzo8!W(60'
    '3tOx0)d*{fj+_ac_K&z%nO_&475{-Lt%Xb_h_^R!oqUS5ly?<r3KpF^x!D^G=u(K6G+4-z86ATXd?yxF=T-{3AoHeKC7zEE(JRqA(3~%+f(<t0Y-_{$hipuA'
    '-S;PO(+&$SeC@S^;uMaSHouAv;wKa#6uSD&2PN14{V;0^8mzve2hy^r?K*kDTwYBU89KmBX2Zp;R~z#ebVle`Bj_}b^Gia-WVXl#HGO`F&A^v&k?~wq4_!Go'
    'Toa*;xG!i|grifjqHof2<=pl5qk`@U`0Q|k(9d_8k76Fm8v}HL<9mZ+ZmmIPJ*U*t2*I4mQ9HSoeYOVO4bWUzl7bL1Wt7a7@Dx52dC<Bm4O4-Ir8aA0#$V3p'
    '<At#rqmL!q6S-Y;p8+3IXxyLNjP-}`xBH#v6kyzMY_}&4cGhrM^k4Xmrt+3DqobGd%@}^ezYEEOQvQfn;Svo|F_{r3gBD}h*!3_wu)wZpheCREHO7c)vN7YQ'
    'O6~A@Dfm=bfQo+xRtr%fUr+5xgHBoONFy~bd^D*r=#GNx%e(a2?zon(F1A)F43aTJ`A;V{c#R+#Dn>@-^=9AOIpdGsOs){I^g5fJjV3qIVlo~gi*mP=22*U}'
    '&&z4>tb6i|5>Gcd;Q;&w@?xbMcqR<li4z^7LNIpd|0&S`2a4#hjt5DEd81-0W<*6|;5+#LZO$g}?B4SkJoEAsJah6BoOk<^(J1RL+&l&6ltIOR=Hw4JchVG`'
    'lY5AjO(35=;JhFJ0$%)`IKa#WBP%dSj*WG1;SYZTTGNW!NK+=$xWieR$2p*TL9~ayXCDO@Sdw;Pvf0TQ=ehqY<Jf<td<gdrk6)5UI*Dpl=68*kycR(I`Ttb_'
    '`Oj7X$ba@f3Lqa9pLuL#*<X$>Cl94hNh57T#h;IczdXN)<Jn!5XT-LYl;#_;+70F%$*q8zp1WrvDToZhjrbK&f1myJP=B9&ZPedqrSTma!}rtYyM}IP4yX|E'
    '=~+?W#(yCM?$^V({Tr1wgi5O+zFb!m1y?$m7XX&FTNXHJ`BfW?9>pR!34D=ia~x(-=fHJ8A!B9r=u$fcX1Uz!b!s)RStkzEh*+!lPa=yctwqAtI?~|aMji=K'
    'kxJW?X3|89dL(GbS#BA44I{B~h_@!3^wA^o+ok66q=;(T7eYuszB66=W*zj=+dCk}$}TKM*|U)7@*;<iN9WZ~XqxaTf2M+<lDwmc_<(z<FO*G-6IB#KbA~75'
    'jLzKYWHNFfOf{$|9aXDQ!t4*VnBPGt_G7@hx8$7mn&sis$@og9oO419!iaWS`;k%x397x0yE8XGx}<W>x?K;Nmh{$nm~nj~3gCnlKNlbiVTMfi^LuG>KM!qg'
    'RYDD~75r0R9CEi%pu3^9#d)+RcD*np#DE%VcPSj?^|HJf^qO8`(hYKDnb!g{?^S43C+R%&r?6{OKQ>@bJQmLA+2PY*f`VrTi^tK#6lwdzBVPp#*K5nw9xdNp'
    '3f#_7Fok+ax+dgD)H<$MwJu-xYxHNy0P4}7J~L_{q1tkqIuf(0p8F>abFbuUDnWzN3dSA<N#543$^5FfhSQkd8h<LfSSSW;1$eQ5o!nf~G$IG&UJtSW<z5jk'
    '{!)=j8+MJnu$6Ob0U<1LV=eZ&yH_AIwUGj5B;|X?V^pSM6>8`VqX-&p1?R?c5YMGHx1#YZizdhiGF;x-5qC-SLNN%Op2N!`hnu29FZ-@u)N7xzl!3!7AqoGJ'
    '0OFiUxjR7Iv%iGt3$NbeqobD^9}aONksL<vCX>P3q~OaUGI+7ip}LLkmeL!mpG_tgf0_a8<k(=kJ>=idj($5PJhrW75^Zh4Kie_C5l^N21#9yhN4X`-U^Sn0'
    'anmTH6#Qf{NdFAmnDDc|ZA`puUrk-9EB|Wh$`T!)(eLRE6XKNh%bae{L6%Tx9Qpug^<9ekyNK*<i&dlY3-o(yC|~bi;fG8dX|Dq8n_bybBmk@^j_*^qR^q5h'
    'q?OvwN3&eVj#M>y9}>jwj$%$+M5_qt<-WX$?&e8kO-nrh20})r;K1(Sc51b?;ds1HJYRR)I9aO7we6Dyx?4-}s-^SBa_uVa%}ry$^jDkk#{%NKXU+^I$_z(c'
    'onx}z@{L)dAh<V!>MHtL4^)H`PT(peY<!F3q99V##fT`LS7))F22(e%QywcLdV}}9KHe$R46O?1#t!T+nZrh43;T*h|K>9q=AwGt9b2MNjf<NPsUC`Z;_13|'
    'wxwB@!qw0xwNlpIX1F7CaDNtPb=?zz&Y*9@LLj}W7gkHCRL`IM`kO2tZa!FQ%Uk`93n~-e<cY`Kv&9BxyM=8R6x2WR8!6Rg(*ngd)Ep+m@h!yuKIu(+{ow+&'
    '_RWSUZ>{BWK6V%<@&gNKb!{T3`$rmHj9Jobw41-!R`ssNAxL`NPr_a^lWXg0om8f!5wuPU-rbyrMRM=@d~%-0A}iaM`J1!~bMf@=l2gdd&s$If&SYC>RthUc'
    '=@3}8sY6v-rL`J<z3bal`{cKk&%2_7(=D;fx1MA21UU_wZ?N%Yu)8JjAISbv6?QTROOa-(dK`|nqrRIEj)JdMtOB(a$KKF4(OKUPvO!gf;2L_@Jyq`1h7&}!'
    'w92h4fxZXSO*%ILR-Nb?;sOWuLVemwdNcw)DROdIS$P&1MX^;Sr#xLBs?AIG;b4U1bZka1pHqwJMRql2xFh9_pUTxpaYi8!I@Ml5zTa8pFE!s;&z94QEmw%S'
    'ow>6@Ojq-tRfs)1JbtRPCA^zV;I{k$cFPU?8}3E8XZq(8IHD2AxTqAvYo$7ug43%RYC|$oVFeUprCPD`Y&Q7wawR-_y2UAnV3i(i$%8jXm@Dx?Lw+6~ym^jK'
    'nw#75<mK~M-Cqt!kM^KJ(9QJt#nI8PKOH>5Obe>y(QEkj6)DlGPmbPJlc-7_;<$WN06jR6{B1r|z4`6UZ}O-?N*#Q7^7`-zath)jtUS{{Rr(VGs^4xP>p;E='
    '@N0(xMA#VtexhU5lx#*@gpNy!Z!7D;d@+LuSF;SCJvjp2{<HXZi=Vr0X2)sfq1()sZf4tUMri<@c7T__ahj%-<GgNc*J<p5+t{{lY{zX(sTm6!`>dw)+0pCn'
    'n?GK&H@<Y@9y2=JYaWMt&)%?V&W0~b(qK=w9i>30%4mJh2V31i)(4h-f>BHrtOlPEjI;hV%Wh_H`zU2FK4Qy_r6bN~X24=}8`z3usywJkrmleCc1y8J&@1${'
    '7ygE#mvp2MrmIw^RPhQ$DH`nb4DQ}5%F%!lOnG_+?f~2_4>mDh*J_Cvl(HGW^+tVmg{MVE+=a7+eo!=WD>UKo<CJuSa1kzMy@+Ni;!iN*0DVC(&`tuA4fAn<'
    'FK4|Qo{&fhWF{m*x`PUp+$h}c8`olg0+qJKnX(wJDXhgS9D8G)_d&$F8f7(h7$Zy)@c^Slm|cvqu!jE|>AZSl35lX0i}T?;THH=EStraYG>)=f|D4>+9;dn<'
    'O!$e@g`N>nZw`ab2C`x2{oaVv5a~N1wgNX`&h^fLi=fS|7ltSdjF5;zxoY1Y9r`jrt!*K%=w`m%@L>OI15T~2KB;@3MBm8+O_qZQ%b46@K=F@PEVT?0JT!z6'
    'u!*@oYh25e%$jwMpwQD$lCgm)L~Sx<vHn96Q8>+fVJ+Cp-s~Ml=@MSe1XCGcWU&fpg9rcO&;Qjz7GpRgblzEZosF*uq2_8%+zm-1V!V~(Po?Kq(<!a!)tuM8'
    'Ho2O?*#PMnoeKC!iKetJxbVTZWvk6Sl+~skp320lYfs+su)32oBC2@Zv=pnL2zraJbY+ffscZK$gELB6n%-?75Xg2?UJ^>AZ3OgEvC_Hx7TK+r;Uc?TE5`*E'
    'H(4%3URfipMRscvTlgwIsyD1{R7o$g+hE#@Z_Ntx_JB@ivq(ZsvzbW}tIL6?Nb?YLgEeI>!BOIOU5Zpl*i7UiQCI<4esUT~W#g!c16DQCCL_Vf$zkdqTFc27'
    'D1hFFC0;5(1g>bM17sM!Ov*fS;oqof5HH@iBx8V<lVzscW;Q!altOPjDkYiS#VUnUE`1WKTb$EJsz>}`-r*391X$P_u1?axPKe7|v8@%Z5ycAzB0r;ZQ4M+R'
    'Y1O8`bCxcSO#RX|(6dWMOmD{NS$M9$jb4igIoHx<)EmvR-r$yS!{EH0p_ek>zHm3}MLpQ*7jVDU=R^2UZzkk+b~WZY=E$32MVohZ4xkTgyS6lxa@HC7Dfkkk'
    'c4=%rD%9WR=qpX=gGUeiNxWBBLRH-O7vyc-u8YCyzT2oQL!bv7qtxNpg2{!PH*1L|4QsHqY53btH7&MF>m|btu0nOXE@z}Hn^X&0H{&IU!AlRu!UTe@MWDXq'
    'u#~v?$(CFJXG=Gv^V4`8(9gr20KRA5RfQ8idtK{-a|e<H>XlQO-T2&WaLyIiw+bb~>>o53OfvsLQFD;c&<3wSEY=0D;A;5gyemEpvZ)@zm~bz%z$iseftrbQ'
    'g{OJBpverfViiE#^1dz+*c1oNx+LV76>Ji4D(AJE;o`gtv*IvBWG&~MTjB>;n4rs8KN7_()1oCt8V<-JdZ}DVgKf?kBbcH}-kwwKVo{^G@oltpP(}13=YkJo'
    'Ae1*V(;M#8eJ@SrzuQRNJ?w3BcSGAR{YVp>7T#{fxyTkZpw775<7?z(g1N}x_^NdZoL}XAVd{c%cDF*_Cmso8$)hN|nM9s19fUD}@-Ep(x#B{2C2sa{VN8d$'
    'T+N(cp0_8}zNh`5-gVI@1P=iP_Qjg&bn_dUilGayLP)qVp5it02`+ZsZUi3S39J?Gr+UeLDp)r<NLC}RLPyW9bW+Lcq)P1|*>h&aR(56m;UKe-C~Og0OLE1o'
    'T{6d4w?684ndf}beJ*#oNUa^mF%z4}`C=;UigtwuG9Z(U@w+ZXwNPP<#tLAt;KdLS7ql1x#K?=oW&jxeu{vB3Dd7u+IE#~XvyEDM)wZit#Yw5mKMbd>{se9t'
    '+IRCxcxWG%BT3^@$Q*v?B0ny7-v<P`ksIrpf#0W#maVEu<O8Fu!M#8gPbH>RG!~R8fTD|SLyA%W<c2D^S(T)+`F;YoNaeeE>$^cE`VP)v5{ZUkBKidZje|bw'
    'kQ8-G3#={-#%|Vu5}34bbnOXyxHx7W&!>vbVJQ{Q?P(iSxnP&Q>kY^9IhO8_gWyEPBTqhb$*09B@mN$xY_$5GMnc~t$W6pHJAuRjC0e6uqAE1isH0gaHat_m'
    'H$T@r0`5p52hjgpJ5UwVrD4ZaSG2W^j=1VH{-7F>EHqI0`$6B<)U%Cfx6yKg^DicYjFuTYy7IpNZvOwtPQcG31+z?qYd~L8(T6OXN>z*w;80SrPZW|;=(|Li'
    '@h}S1efV+(W#1AN+!DYZ(JH7Co&&KH`|n2mYv&&)%s*c9wpev1%`@P;Wt$o=sb<5No?6jX!<e7YXy}@tuyjL5CA6Z44NJ7p(rV7V<4c86WubNN^0A8{ZRAeR'
    '2jL7lHy|WbUSRrWvysreks{W<-Qz%xIO+y%xzJ1UI6+n$L%?-oIk!Amqk3vS`QB;O^ThBEjyBf$ejCPFxoB>+)3Qvi_$;4@H>B;(>@%<5Mzn>nqhs<f$a=HU'
    'Fq<iiO0w68DhPM60-4vonhHS+16QNk)06sc^zDN<;5xK?711xLV7mm}t9Z6AVVVu{9Gmso2+y{6WhLKjG(NNMxGZ<x<%^v@{Vtpoc+uG%(8q3R3qkiIyDIYD'
    'bj$$8G0qmV?M7m6x9~9yp1&6duX3YN&BKI=FnTkArf2u-tWH2keGrZls@_%0OM?vhVI0&uo&^H89v1ZnkW;UH<W#o?O@vzZQV8c<!f!k6k8UboY|KpG^A}IM'
    '#A$l%tKM@X6fMq$l^eyEAAW4Y@;X-iqN6Vk$_Zt-f1;e8sYn@d&G%YrO^6Qag{7xkEuU<zK8V0vaz_J4fiPVeVxrQ~-jleTNr8baxBE+`%QT&vBC`H1T~_{B'
    '92D<uf~ebcC{hP$fI3Nok5%~lTq-DWu>b$_vs!F=!j*0XP!FOz1_sz6!#GMRxny1(rxgFIKpd}H7Zq=jkKk1$bPO*AvspcJg8|&=J3HKeg>0|R{wwx&41fp_'
    '3z;{9**e2jGZn29bnh!B*)v7Fd#y=wqP6l_eq(la!2WrDI9%c5U`S#y2e}d_xt61_Vci_ILkUgy>@>Vz>@!>(gU^#m-RZ2CAwaEKqvZV6)6htB=g;!?qSI%6'
    'Q{vt0h;kG$GP|gG4kc?TeNb4meEo5^Fx^M>wU9r3HMG{g%Gb8aTk^A8$g-_dLHMJUUj?DmZKmHHM$z(Ue)vX1rJCsey?Swqyi1X6`$nm!CkWcZ(h}#4OaAo&'
    'olWg)M>?;Ax40^X<3g(kN|71w0LG{*EkI*rka@K0Xzgl?0r3!E2KQ2nnoL$qAg7nJMHyFQPe}_J`mwPd@}qVBl{=2Dxk=G~lof>fPsO>U4gPK4*lA<6(YTaG'
    ')x=JvX(L_<RI(TW5>rsZONmpTvn?*Lit@Y-g*)mdE(k}mjCt|OxR$HMu?aiE)Wr|x@aU;IPEKwmq9523N0lF{%NQ(t96PVdvR>)K-k(fwHwQpj@Q-jvh_Bo$'
    'X|^mpB&V>xYk-KU=s%n-;OOni+k@9CMucNSRHO*Uh`7Na<Ty&@bb!d6(gsX!P(4!+A`%^Emsi7CHkSyN-s$8z`x?mvPITPJ&JO>kun~?TfnRRa2s{V`jlfeo'
    'K!oJlY7+Asa$7$B?FD+xSI3i!;pjtEYP#nf0w-P$ffFZ(z&z)h508v%KK$@J^Wn+qZ1N!+o8N}G2QmlDom2z!qC5igzcF5{xtLFTH<oTGiJSoKKNoO+IY4+R'
    'F!)kH@FE~^nby0*e!EkO;-721`M|m(HLL%@3<~#{(;y=kqF~wrgQ`fR7G`2P?0>kL&LwtWZsp6f1)E$_gp6Eonro#&nE%gCgMjEIX%s;CFU^*4vP!mulXbEs'
    'I7t%z<GB$m%uiRx917#6J!$7cU{IJKnnxbm!fMLKz`(~%g*y5+)UKQXui<5Q7tpH2F5RJjMyb0(_vmDnPs=%RM67rFqTCRLStqE4T&RSfp`qmFlB)aXz(8U~'
    'c_e>AZmiUt0tal+fOz!oZGx{vbfRkfBTY>#-$(Q<CEvuCIpZ)_Ln;&Bf@5jjyu$lVS-HTB!-)9Oe5&wXSF*9}K>d@(Y-dS0y}Csd>k+$$5~On8(~68`tHE_S'
    '?yaP;)pw5P6?=Kr8^8`&C_-C#^;Tb6n3zZxz_q-j)-T!4^NPZfPAD4b1kF4IZYt}h>hH8$%}yy#liLwI)vb{AY;7$YJ8cx1oUEb2a0nh5DI;~1fsjussGqG>'
    '-qOpD?n~!55jq%8>FL#?tJBkRN1+EVj-LFAVCT53_HyGtx+5@rXVUY|{}k=xrB=ruxwZq8#@eoEYgYjorzEV^a9{QNS5pcoL8uOL+ROTr3uq-mzcX@Z#dt;5'
    '_7bo|&V6<=BmQ)83Tt}GtPKAR3w+AXXLvN|oS)*%;IflO^Ax6c5zbUV^_GvwJNwim<A+UV?RwL{&0+4_>XdeLcRT(*;|LoW5->(X_~%karG63_;}cH&1*y7*'
    'Jf^8PCWWNK)rQqG?r2Oisrt+v4i80<n2zcvkHvjQXJ5U~Cwi9BOr1KEz-;JFiH_SF3+;Al&%5qlQd-fEi`r%Bl&LNeEzWLTT78N67{<j@MO#^F;~a;*(R?Cv'
    'H3v$B+J-3*K~y}LeI3oGqv664L~uMRanQ-vOdNFbm(x!x9m0L8r&XN=+UatYG~JTp^%T?<t+r4#IvQ$EdwpkxwbrjFeYK@xAssd8SJYp&vRZ3a<Og?QMU}Pa'
    'S>)68G}ZT_CSC{S^o|~g_k&RSZ6pe7<}Oh+InU{pL$<qs-Opy1SF-=D!=e0#?15|81s$2kQaS9G)mv^C4Eok+`=GaD-N*n!I8>Tj%h#Wjw>}SlzYz^6ylLPy'
    'M*4aj`4F2F_$7d7Uz}b!Uv+o#AqPsYb5&Rh=fJXj3x^uc=&XOPl<`}Qtp|-q&FvqK4^Mu3@#bXnV$dQOuxRHYc@WNxC*@>3x{ap2;ea?m1klLdy`wILTEY-5'
    ';Y%abdNX<mJ*{mtldavI=putUsIf=fR=g)wTVD*3tDP@41Nx9jmx`tA{R!gIT=|}9jGrV2x|8^*IZRpR8u0~JE}XQ%)91r}V1<4W_~5rub4Mmo@yzzf$lFUl'
    'zwIH0%3?ChS`p4qW1Hru;LPfMpe6w;v(bmN)lm&;Ek}-U{niu<#8Tn{B&{%&7&3upQb{b*Qi0c9I2<T^54Rm72gk}l<+H0%=D7Rk2$~m?v|jrkij$65@ik7H'
    'g)ucr<eOG=VKs#NVFlF~+f)2`>Ezr~bd5t_tw<Zwmx4f>Pz?Hw3ar7Ag)c=ra0WkkEZR~#AjJ)x(S|#YoPm!xZl*}l$@&`GdXP5{!|GrIadFTi)?x|eC9#j@'
    ')=u~WL?%~7#3Ukt6n$K}<4dAszAV+uGUWBrD|3a=buRCP1g$s)rB1#prlcvI)$s(Eq>zd%slK%8Tr^V9@qwn)+9{fP!XpuPeC|^=wfQLQP<y|??*YRMn)HmJ'
    'C5b#kO%R#Fwbodj3FytqAj43$ZW8I3)%so%=@1b^3?Z?lp{^rHgcQz@qcLg~5(64Sz~`P;j{2PX+9!k}D%qe;-Z#tbzq9h5zK>&KZ@9uc(Vs4@8!Dc!do=U}'
    'CrpPUm@}m}HW_|eo%p|CB1I{8*Lf^7NaeSs*8i=uEmb7KohCUPWx=*iW#&vQ=`;R|EtnAO0&*Pam98z{r$0TH*taTw+Ieqw4R<i%;3<_UTk+@$!h~8N5MD$*'
    '5)5xaphS>Fk`d2sL=Kq^Q7p8AxqzLBS!>Va!esv&E-kT7t$q=Gv9ib<y{{9Xvpi6z&@;0jR(AD}oubg4@k%UK$rt58H+KlNG5IuuM*aH_l_|+jxn|Uim#{Jr'
    'II}_k&HAFmSI$~l5=T=KPqX4JuzGyW@;Dnk{e_`6D|V_R^k$6^oPx7t5@mYdEV-k;0E6GtTHHA)<;hwe*6d|{`1|Xvhp;IJy(xK@!bxvM{SnCX^>;nQOrG~f'
    '2ql}<vkU4tYb-I5WPLHb$lwC$XHkY&z{U~!Xf}K|9QQ`iMTYRR!}$ezMIW4BKz%=9uyJ(s?`&3`D|)jTy}-5?Q0FNgk6DJcy?Inq>f7e-Zj7q48?2pBh~_Y('
    'S^tWF+H`dM^y+jp>__CrD)5WsXE5=K$#r~+0H}D=lfySwO|L0QCYkv+qqpaHN8y(Y%s8Bj&Wg~aRR<717n@6>f9!0-u#UGMh)-=DA5*6@O*t9ek*4u{G8_II'
    'o;=(mHwU{J_%SwZsf@opo^Le*)AQ>LHUazV`op{d-UY{mtPK#333Zo%L2qbuH!$R($k)j409RC#nN&OY+eimu2%vCun%z$DqD1WBKHTzGygl|%|IK*BJxnRZ'
    '8)%OnQJZ|#%qH^;_yj#-Y=UyQtJUCDpsN^usCkloh5(xrG{}&79qT}~oZuw9gR#Rd>>dMeE*9rhEZF?)+0pUye;&Q+K6!EU>M(uiKR!Hpa`58d&EeA&V_V#J'
    'FP|SDA01mSp1(PKd6L$u4D3-&s*LFYe;7Cq_(4D(@ZZB<e!*YQU;GOHK`>*=s6aKLqWvWORAo(bwN;bCgdb9kld943<4dVSH>ZnP`f0xsr&CbWsL!z^bw@+('
    '>;F|<djghphbDv3-4p<SEU0D$9y>OOa3xU6h3%(aNzY3sm;wTL7SZ&ce$v00Af`mJ@#J)gv~hNpw2{yw*<9{Jw83=oFa5;OIP=Juqq#ZQCci+NCx^hBrrp{0'
    'gD#)@OnYq8cbYZsW|vpJ5gCQ&3HviBUK<WfLPsN|w{3pgN%&W@F27x$a%3}Z#_cMx{?$(WnA0ZN&(f4?)xS*v7A&k1>VeyNnn6cr4D9tHv%^j2sckN&dZ48}'
    '?sDpTXH@xl)dDzE4&{2-_K+NSC1@Gmf#_4!GV}^_ocD`#YKk8}Xt`D6_1TDXlkI(#?y%Gd%y0Nj0CHFJ(~r~5N4xG+BXMOlos-1@uD4W0dWeDgyPY&`c!0=~'
    'z95&^L4h>QQ;YJj3k;M@aw#C~WMA}M3(@f@>N{2N_!L9kh&N0s1S%P)sh7(^^>-`KVVzOTkk*o>njw^ZGk17^i+3qzg#gay(RPb88*me5W9$A!CNO;0A}e$~'
    'oLn)0v$;Vjp&;CxaJ9p?e6#f@7Z(!_pi$1CXf9!vYJ!O$hzl5U%W%JEa8CjIfOq96>kWRenTDI;crdw%YP-yu#9BWw_v$&Dj7Ag0Q{*<`mZT3_*6<WNCwT%u'
    '4w6=>XT5W18~b-PHvs=Q?3AXE7NLs2tMMNGr^|e)|5hGX&BEhT+oQ@Vr6J{HImwmD1gPX`20n#@wFXVWFTP2!P4)FgQ~7ntcFZ>pY>!LJm?NqJLDC!%QZ_8d'
    'RXdLfGe}<Wk7`F{V!0Wo-YKs)6X_nFSlxH>fBF<c0JA2L=UsZ2w0+PXgXZu!b&;#mw2Jas)kOpIP9b)otzLH0rX9tW24mRT&izz$x=kNBRej1S`fv^~e<u)L'
    '4FfO7-lg39)qdKDtOn@ts%(67`{Vtz*~;S-@hvM5_W~JQr;eE48@NbzRZcgk2Ixhga)K{rMMEv;a>iiDX-Syg<J1q*tJ3>wr_=VmhLw~!zOAvoK`(V~nPC;v'
    'l;%sTF}N?eZ4}!&(~P8yi|pbQ(a9u@jL<EiMM5PN<n@4vPeM6%sCS5Mb{o}*&>)Q?^(4BmqQ?@7QAn$}l-+U-D@7n#Tab!d?4#3Tx^;Fn!*E(dzZ7vp;=;t-'
    'Sv8y}voxWQFgTDZO)37|*hN)nevMbEYh%}~3l;jYqBuso?vfz;LYt3!Qy>fuopTXy!<5RYml)wvikfHw#$2<&YTI-zPK2;I1r&XYnORBMkI`-c&rp@!v8%58'
    '7jLx$&wN^>Y*ce$m}&}p6h%x+hoV^5fprb+ou`(B!0JGHmne_4s>lIVeY#;?&mU7(7m@!??C-Yh(>(8il%5uqjrW{4iZ-U_F8q<KQC^g=2WqiQsA3u2<}-^@'
    'XY`Hgb_y9;834Iy2T*pxeWgmBy|k>KMc(4Y&f>&Dq$U!;^#fme)$f&VY)@(^*bcr2IO2_ZPT>2gF!x+>&I{bDT+iSq{-6a^h2?@)yOZc$*J>oy5fIo>wG~iP'
    'B+PKN$S>SsujtWduh%dQa2weou=3jeszR_Qmht?g_@6x`56NgdX~QP(q=kGKT@10V2o;Ylq}ar)-e6=D<0Go{DVd-$@Qs4v-JEdnMJ1OFj1r6r)(tqZxP>AH'
    'JZ!JwG^+IoPD5X3v|r;r_-_vlN0Ged3P+;vgmO2S(i?A|(_5n+6)hul8A=X%x0``=@$rQ6z-LRuXj?0w^#DNc5kwSTBV*~w&hjc`_n}qceb-4t$}Wmj>7CAN'
    'jC)Is$94VzO~vtkV{?~<+rZb4-4+BEz<n4n99tU~7#`eZyfvVYc)XW&$ERw(?mbXH?_!V%(x$VI$AjK%kh+=NEqVY1*v-^Vq~t?#4U+FQ2M#6VUf8ZxDF*Ol'
    '`0uQmG#hbJtI}C}oz0&1ZmS9K1MtXB43EXA+(qx>OS)u_2oM&&cmrQjEu9>_q7Kt~Y&9S3)8X5H@aTc4A68J{lq`ZpH@um$>7`!S{Q||R)t7Q9eMxr=d7|Fz'
    'mF{NU`d(=D4Ot5eEJwTChC&rO<kYJ2PFqoNeuX!qeN#Cxl3UH){lW_ow?#|WUBYC3LDxk!U@PN`d4YJ<u_@&o-HEUq(&;_xvAP~RsR3_L<(z5q!0+!g%Fsm%'
    'bfC9b%xd<~ld3k@Rgv$EgXTTYw3pho%iFZfuve*6e#YzVYDQMTcQb^w7rBh@O|rB^^ASv0)VrPx5ewo5Iz5A%bJT<T@*G7mlxG%mxWcqKZ{9o07PkcT3lp)J'
    'hpc)DUFN$FH>o427;kR<n6ty+Gvba;L|KmyL|M<EG0g1a<1_S~m<O1B%1$T{o@w{>i-T9M4v)LQvsQ&t(SE3QSQL=!v+c+QorHgKC7Me_%^m8SQ`_@K>BHHh'
    'riz|7)lTxg?Q<hqYA-sA)A%?loIb^TODlO*O+S9zWWO~Q-EnMhsx7Xl-6tgs|Da~^fu#~XWzj1AG-U{zgyL4Eyg0X0sL^8?H;@F3+7Q`nnl$W;m5dkNcd?>X'
    '*99zERbyrNgSiYTp~54RC#-mq?gs>Ica3|Pr;>bX^kJ{rTOyI3!#$a3flz4Q4?k?}z?DlktaAwM3fygo2cwGzBd`-K7)jN_cUwE(q+8pqKv?1Z?k<TLLk&bf'
    'FtfSc7Kge767|(+kp_X~_SoV(NG-kSx6yHSF}X&Dcb2is5d3j@MXq%H9zr3|G7{0r#y~z$vE5rtE{6T6kEUHRzHge^pnFp^+h4(=k3`c19R=EDsz!t!$*oAr'
    'caEJ>lnblf4Ca%hji-jc;Q;*5dUw+trQr#Q_a;L7(h?dHhyYF7>O*5jOTIVH#G2LFLo;`3hg~i`a&apN7SP9CflL35CKut1hv<}+=CK1%iG|JXyS{%x&%fK$'
    '2X)`0TFH~IN}hbxpeLWoUF19E1;Re7m|3VAyClNA#l^<AL^Rx2bZ>DiD3%BveeVm|LEXiKzKL77D$1Nl1I&X@Vv&~TSf$sF=q(n|bdskjRR`NfQ^Ad9Szq-h'
    '4G{I@rLx`Xcg<EuA4}IY*S<=DMO8$r%eQ$~96^wI!G*@3eo`)Ml6?BPe&&#j?~$R1z-OHeKO*u5OcNd&ki=ofEp9bg)T%_i2toTvTg?0&osIaX2^?)PB?!BM'
    '%o-AVQTj*OkhHxxB|~6SfCZt)XvU&q?-NxSa3&X+j^%y5Nw0D7>F?<jDg_ql<{TjgraF7;dG8v;_iQ@K7UVM{9o@|3f6wQcQw|IIqk3)YduU9&AKx3I)YQ`j'
    '6e;#+b~sT6V!3Ku$;j4p6&b@qMljsD&7B=B7w(2G1I{~=1`JD1J{;SuG>;!YB6%1=e8{;G!}r=%EANSR66qvuwngX%mS?Ec7V6d-=B8zK71F>r%Zw{rqT^rK'
    'ww0vd!nTVny|8hrQlttLuVH3n#cNxt>dqeh*gd@(P)-uqF(s4e^2`PN_1<{+?tGDI%jnj&jl`JNYC8#PD|YGMJIOBny&J;@H1{6|Z1RnuXj`0of6<%P=vBh6'
    'lv{^2H`sQ|s)<_b1XEvm+a`ZAPHY1hf`L_AIe0G%gwYD)oVLs@xY-912aIu?IB1O1So?90fqzbo(=*|#Ip}KfV~woFO!;Ka7yQ46Qwvs1ueL%2)0mXP+7;{<'
    '4dw_uSAv1K#M3;|#ED)QJ{{FeuvulF>@h`6MiW?E`f8AkhRA`j^R#BDX=!4ei*~jEc`oG<;{?>X9^U#w2krc768}t}MeLwLe?JB;ypEIS^>6dKHv+b=7RO;O'
    'dcH^tE+SR4%8y4!BUM1t>_e4u`ua0ok2Bgu7LNzyls_|EpRZ4?r`U(WlgR%mJB(AfeJ69+Iqfi|)Z+lU;<DyaX~$l6(vEjmUVPPfyhk6(=WFc&<QefRZ^id<'
    'GpO6Z^oq^r8%-?1$VkKFQU#9dplkKr<zwuM7Dz>srShhy`m50FDs2$QSanGc0z4F3W1C5+=l;fVnJINEb5&hl16Dnj7NoEbET?MEn`GsV7dx(An!6a$M3l4j'
    'E^DgXzR=LNr%Yf*$@4V~Y^L^rh3&Ji%QnlS6m&(baoR|N3!Q(iK=i%G0>cxki8jDlZ!~f~Q~I=!DNS~-I9HLf&)v|z85i#jE+9eFXmgS$a192oNN0(aB23d@'
    '_kcXsRW&=U(oL^t0XM$-XsZ*nH<wgnW-M=;@obF$O?I1v*~e$l&nIw)yo3`A&x_1CEp?`I!ht^30UecoC%O!gAPV)|!Bz0~CYe>Nvn1Yr1%)l0WatDM6}cf*'
    '<tlO>Nk~O*YF|Y~&ba!~_0A3(Z{J<vEQ_ECq9EzNx0=b;7RZL8I>%@At!*^x)-yU;lNmBH^lel-{QY&kxw{ibH<PQ;AR1g<Oe2+h;LW)z#!gaJAOu;DF?;wR'
    'oA*J+?Q>x11_SvGXq^yH=g}k6ukFp~MB+gfWE>w&5b6s70U4TF@<+mY-x3F@t>Nf_Q@5fuq;2snRlzbK0gH^?qt7Uag{|=zSn>Lo?z5wlH))#>3LO)2_AxWA'
    '88^}+z+uBQm9^`*!yt~`KcI%+j!)7W%yG1}71JXXOTiHZkrN>hsSt`t;uInk2*BSWILgz5KafD+uY==Xp1(@#54g9=u7HLiS_U!8q05DS#Fw=5NOp0nVGI(t'
    'UG+Ag1r7@3zT2|`DpGTxE<IFB?VFLP#~`CVdQc*ym&3(*a(f(>+|y>`&Z45tfOgjrI#f<w+UB0<G!|{iY407oxrWRORAS5t=HHneXXLS5wbxQD<NZ)rsQyeH'
    'xcZ|<b-jZOYfshfr;RWdPtI_jdP}*(?NJzE+75Wa3gnP*{U^5cIb5{Z1=aRpMPbSTr^f`asTrS_9}Y|JT`q1@N}5X}Nazy}X>@TLc3nlIhVt2!)2XrG^1ijO'
    'jka1eRwY*}Ee{odR_x1-yHii$v8!3t6YZi=<Dub@PnbVz?{47V^df#7-o=IhwEgqXoO|fK;n-mVQOvDAUfkF+4xYQWp$c1Ed>1brhl;Gg(<?K&klr=<`Ttrs'
    'mX;cK!Gt+9D9_P^RyJq54;kOxHM02(U1g4sP*Jl4zD-VIDrgZA|7JsYDoJ?q-hELTJ<3&=eZ=GwXhfq+9g(8y!2e9)_Rb<aS$qW$qpy9{2HAp*anu>r;y-qF'
    '{-BM6SQ2-?wW*rp!=vM;hsWJtIQNd&1l2o9z(Xg3CUKTgFSTD`<UGZGr<5d|9$WIy@L~$o5ed+YvMC_|2QSOe1p3G_q28U7IBKnX5>0!v-o@Mq#q6@0)7KY$'
    '=e0o(DbuKOG^QsAZ1<rh!;R&j@Z6FYEypn;YkTnWL@6sQ+xiD=Z_%f$C$4=&IBRO9s*yAESknlZLw6+i$3wiJ$`#zLlxctHC<dHfyR?kUxT9BlP>62#B1?q*'
    '=z_#dv)4%YLZx^77rk;<p;D<FQ)stq7M^CaIy$37KhU3Kz0vy~r-^nu4$V@MsqE-AQpUkYr2WeVu~=!2GY%!F%`#ZqtBiW4{)WEACbkLsul6hsCEn9`7;W*F'
    '=aI!pWc|iEI(t|p7NkuK|B`F|@+!N^Oxhbgafq#AJ)k-)#=t^kfm<E#Hm-<KRjl6#>=ipX84#qn%^=eFZ_lDkfq<M{E3W}ixnZR4X(wd$ok0D%KzkU5Xkm4G'
    '5Ht_l7lt5ml%27`&(r(30Q>>3HNsfY_!mWaS-q=(K57)ANR0{S11Ay2M)0|W!89QRrm;0t7UG<$I06uDuwJLRY%mKqzj_?)HX6`u0G)%RutDL9E?-sJ6YxC`'
    'DY#ZMn*pF4z559L9fiFH)JKA?#Vc8`Ox$~(O1<VYnoOHy^An7*qNp-WEaCznW)+yG)lpIP=fmSS&tE+M=izZRUa2#VmVJ4jIEPqSzY2j$^kxdWT1c<(T+EHT'
    'raW!xr@_s^7H{4kmP^j+8{?9WvP?^GnJ-NTinqgLs&Xf@76B>^6NTy09YZ`H5LM`pli!-RWHAzqGs$};ebquL5id#{Ux$-P<Qr?)NO=&&Xs0y9$5FEt>8QX0'
    'aJ4d=VYdru!KgQ^p4Fvidse&kV7ojSc#wH$_C5*1w~^bBD&%Z6t!}#}LWuuuc3h_5j67P9nSxuq=JNsm&Cekoj~-%*l|J14Xh20F5xp-+$W#G?n6!<<yHqg6'
    'U^1Q{Rt)pQ0_VLLW^?U4_C}SW%r_$)W_{ixx3J#){D-~>BLr2lK+W=EkC+W=T-X9&p9X_XrI^5OraGe{46v*FXgy~$mI=u<{#tmqyNnta(l=x<x%vt>r4^$a'
    'ye(-+sV?V1(ZLXDM>qr8oM#JI+TPVj?ZS4uW4!2~tbf&VJq(0MEh$&mvq-i?A3E!V$l0@pjbKI!M<3#J>9dCo5S(MbjX!syol)6SsJ_H}gRzEoR70R6MH~$M'
    'LS!^+au<_DZ-gwyW+RV|km&YEf27;a%LNwBD}TuT80r)MG9%HCa_v9?7XF=#G%~SVOx+Fn*|-3P9=R5K^WYi<ZW*<xQ%S3%de)*!1Yy%$G2=iLKplp&d2TNo'
    'Qo3vtlWHZ2Fk_M@>0locX&_PC73mvO;Locj4_BXhsyWPIo0Pp<vwD&2xNm_$s^#qgLvtDcAjVZE<Wnd^Wj&Ws+LIf(cPc|HzIHASCIRk+Au_+6tJDo&)`>Qk'
    'x||s}x~*1Js2jJFskpgDCP`GoH*zXs2}{c*&FEPE^qkfYZehdzGwZLUC*|j1re~sP<J^&#a#;$4tkHWEbKFPV-g~z_L#pQO_Z|0_TR(gmlt#9Y%X$wxV~Bq|'
    'XvuhOy7k_t7dQ*=?L_Fn^1wq=zpxivRdA6o*qb<56YgzW6N=F&@k6g9Dq$?hN2Tajx)?rTuKGnQaB><RtrTcT&0M8ZW3ex**9=gdU{W7mqmJJHa9ng>R%ESY'
    'b0R20sxDpS(WMd<;9LID)rZ0eB-k5XULAK~-*KmuY((wg)_d6f*h$(dc6zRifY(jBOD%<DGqxUx-fj~gTyetmd5!fP<2Zb4@pV;$E+9|alp9liYA{jG&J4BY'
    'uPOnO#@-bPG5C%$W#;d?KIf#AvA2elsF+)K8^#yvytTYL>e{ReF)I1%6a)%ds13O8cUx-FuKg9muRYuo^SU?%gZ|zsUc4EkTBHHAr=(9IlZvJ6ZCCSZ-YQE*'
    'du0XRkuw&Sqeko0riQojP&W7QnK^HIVG0qTs40#Cdq=#urMM+uAuHpx<<{gU!**@BoZl^s8o&x#%hu~bN}yCHIwlYBLuHu4eC!gY%gAC<0|EsQA4wdn4KSwB'
    '#pp#oL2CePjEWM>SP|BU!v=NlnCeg48`e(s7tG(sGeK)X*uA-+dP0A1^5oUX4Kr`5KsGS2Eeyg)s{oQb$G!NuQsU(ZulaMJ>`=uhuYr|t@m{S;*?5$~|JbJm'
    'K~?I#8<2ma^K3SVZf1Cy1F`2j9RxrFr65qBP+N31M5xa52}N3AD<C$bGy8z!Mq_G0+&8||0p!Wgzoeh4m<0+hcXZmLGXa7aK6;mB^UORN^ls<ytM)L7noYb}'
    '#X3aD3}_fa*Q4nz)hjX_)cxe>ZMCKFDNmjq9=?X3>^)MY%((Cq;W0nccPDR-?aw5Gh4rO*qCUoa6!P^GoDcbSr_s<~?c(23e!J0-rVbCELSfcowweu%ZrR#u'
    'Xn;%j)WNufat#F}+IpyJvO;M8Fn%rwWG}uf!~O^U1M?fuUxIi~f1ge!@|X5?NvfFimi`!IeFS$Jcpfn0?1m$2Yo2xO6NMWwz=?SLF~$iaF;`okJ||VeW|u#E'
    'qm2K;CcD^cuc-yxo+yhB#{)(cO8RH-RI9jAQX9lngB{9&eD^M`DLhsEj!1RQfk`#*gdH1>K9J>~lYiOBtBDVX>LZ)_DZz~Y4-NuRxM*XrH~-l?CT-&hpMh8>'
    'x}of7_yha$IMpRVE~Wfr=vt?|9cb72&EPY)5p&eI8T_rQ;9mKa@W%D~%7@eR73SHihjL2e2uQ37_AgYmIr&R^=%ftRo8@eHTGJwBFF8${Ni!G@3Wf0XY0}#`'
    'bxE&P8>$WM@GFryt<ZBfBs9-XX#Bq-&mfd)QaAowc}bbekqUW|&?gm9(^?upECDvH!Z6}Q^$bqx=fsi5iY~TkZ$4LA()oGH;42)?BaspD9z|y~HXD2A!x>Bg'
    '&W_H*UZrOeZHd19&=KYHj5)yPsltEtu)=iOcESsD5?d6*@rxun33xb7rs>4VA41j&2P#h^>9u?TVSc^=1AO>BdRG}AEY5Vm?pO-CaKhpFar`|`mE}C8UfH6w'
    '>V!!#=63}rcO%u!eJ>Y~sd2Z_D6CQ`IhWK~E9~n=v$%4++E(Z-7Bh7=OM3g_;MLQrR8fP1jbsb|1$S&CZsXK%B|Q1GaWKxZ6RL_szqlG96|@Os-k-iV5Uy^W'
    'gL@1?K<DPkXq3%zQJMCw6pqY<ot`Q$&pk{VTo|O8r!16ZcuzTEy7XdC$b;izxo7!Fs&{;nYzN9jpB)RY54*%g39Qda*&4#^bIu?Ie!D^7dt*Aw^b3drG@i}U'
    'G0cLp-846K+G1oLX!@#ior=fA<kqI=xAS2iQAp5x8s$f6_8nmaIPe;bd+fyjIB_J4NjgP5!m4}r7Zc^3%XPN+Kkdb&W4l?ZbG?}0ai~L0>@Mwq%)Of|$ng^1'
    'UM_$nCZ?`<&-`6ap`g<V`2Dz%*NLQ9)7flt0aYy~vBJ6$){661rQSoO$VWeXrx}&tRk6KoU3cf3)I5d$DX1O8p>;M)m;EW$Zmud|ff@50q=bW7$z_X`zA6Y_'
    '-Jq$RSL54gYg6x%`g8&d1mf}Od@)>HkpOpk8>xNE8$GJ==|0c!nc>gi47XX*K)vaH3V-gW_QPf;6nPp<|DsdAco3{UNmpJkLcr-+bKlU)eT(z!eY~u?pp({a'
    'HoP)XRKqI=E%LC>E#D9LJjJhC#pd(HY}gx#ulYw`oBlDu=b}UZ$T`DvI&|OkL#K?YEp`d8Q6i)b!fk-=wiXCsyO@OY7F*mKZ=Qr&iubMAM712drWU2KG!nZO'
    'gvevKc$)m<pj7Ce_;9soZIJA=fOHU9Xz8U+6cK3!XiUhaWA%^ay^eLs?oI6Z`8L|#jBX~d95WS99;qC0QH^7XqaPwlX9xc^*%o=iMPihcX=3}J+U9B7KD`AI'
    '@ph45M7$O3?FNh|-#by_Qk?zXKYeg#>H|&`E9tExC6@xKdQ(zS?@jvst0~1C7>%_7UBPj=Hf9;AARTF76d&9OFAn+`qY?;XOmAL%%=<UwWk0@7t!r6;LR>f&'
    '>%APaPnLPS7>|XnUB+SAL%BPJvw90NFio*bLC#kK%QXv!1<|#ivv=cH4#o2CDHQIc6o($bt=Xholb({|UWg;ttfJ!cU^KYMn_BwE&_k%OMUUI~s6){M1*cH~'
    '%@84~G2c;dCj5s;m%&$YtFS_hN`{r7KJ`>ca?hHKqHoE}ayGlbdz*v)iIDo2wT@*D5;gcfO>x{TGt+EvmU2B&L@Rij!X!;r2IxYLeNg@Dr2RThE6+1ADEQMN'
    'Hl$JlT7!>0?=-`26DhfmU6glLl@(CCqERyG3l4}P1%y(`DRo@IG{Yo*W2RX(#xvUpCKN2gE^=6@@{EJHT}=g?bx`ymcytwGs;F1I@)EPc4a5leFFjXPkm(Db'
    '#?JDRqL41S!qqhwL{)-}eI7B#!3x1q-zsIQ-7@JN-5_5}fa7$JRWl)m!<P}}=89~8`3<zf`l;zp)6gUark+E=jf`NbvNAs!T}ND;;Ib%Z`)o2uje5I{4YXB1'
    'I~~2)s8a2;v9y*3_?gath{6E1WY4`)3d8i%y8=Tg?G~3S*H^WVRi*CDMki5!>J+TsMmw82xvB(qNuCwt*(Kr@!%ihJN%j#aCVB)C1~Uc=0OK-7lsNR+i^kba'
    '<ir&+KhG<`O6~-039-k)(|kxKSdT2rtQ8Pt{)PlR{?nBVWuE<Y4lR<+RM`o&>2WwP&q}rFMK~_Yv$-TA1okLzrIx0O`@#{9%jTl4@@?iCpzn*TU!G}mo$=`q'
    'Mw+X~Mc&2u*09qY$hTL#eswNjohaUQaGv;0$hnqd*|ma+L(fojLz~^2k%52QDKOAdM147){vS5j2Ufif)CXCPMB8AhV%=Bj8l7?&5d5u&0ilfGzT(ac9ux&0'
    '8zfh-<eCKzB8KNOb$%QDW9P>RVGf3;tdJn9&SWq=8}>O46K*T?Ew43yj833I&aSf6*m{6#{4G4Y1?u!`uQ!f<xf-K`^oQQNcW}LcB=<vqGRS_IV~Gz?;2pmI'
    '0bkFCeb`)Av#h@LaH~<D_d&9x+7Rsk0}{_hlN%<c6pWIn=tU+NI{He582%uh3<+Pdo_U!u*eLa<4+q?WE!P{*&oE&O=AQh=&I5J@-%iA%8@;eqjxFjZxg$cG'
    '3DzfNME6%`q$f;_HMyGgF&oU)933^Y*##jKk0<rX^oI)=;RU*upP@=|+FP8@6COP2LMe$i-X?X804O@ho?fA8uMhJGW!!|O(kw3-hue+dFAT|Cz(J3CrxQw|'
    'nrZCPO`T_TdwYjsjIadsdW4`}q>9p`H+LICo1!0#V6192DB>?1LPY|W@agV}CqJv2>=cO#QnHb7Kk+X+$sv94)4|DMnxj{mkY!i~(Oi3iwiWXATm@XvSEBDX'
    'cXm|xw^-x$w}QY=**jeQdD`ym4O7=ybKm+pk4`MPY=#|uljtY@jbdJiC}Wnz_vB268_l36r`;JXD@n!gbA5PU)Q9(>KD-a%^S`eTF-%`gkmcf;_wY=8|IVSV'
    'QDM1BHNmj^<sgHw#o&Y>xDo9=&xjH40m%=*TZmS1Pj678!2wb}TO=9X@1}ER6oR*jR*_Gi_lUIRpm(h{+EiZ)>hn4NDd|h|jFJ*OOhYYdMa}ax-ZQV-Qzr?E'
    '+d+7_k@|d{Df|KMiCovG+OO2>?j`YNPUVTITQ7sgTFddR7!lUOHhpM^X>!@I77{A1r<YD*my7A*R^l<3vLS8EK2CvZ4i}@_X#QbHhMrT737!rqfjox>qoXU_'
    '*PC{Qzh($<^AQL>l4BJTG9YSvH5U4{7Y*2wGra;4<EP*L_yO&II7v4c&u?GXB<|uyNpXA|PQ(Cv3&42mv=i!hI<b^vW5mEjQ_DALe(%Um1x_$u6K-;=Y-&|y'
    'fsfpzQf=_0SyUW^Xr2MVws2laKk$|OxeUc(OpewzU0(-?&XDksBOh$Dd<M`DhKg~oTh0(Z=o6#ZUVS00#Q7?o(7&Qq1eCDYKxbktPH->40MgaJ+ln$e3#V7N'
    '=nLmu`g|%dX%Hs1o+O-(bUd-lpCkaw?Y~P&x1PT`c+q`w^z!w=lQ*d|q`%NrtgvoJqq3ZY9^uuVP2s`j;fL<wvdPZQvOeJp+ekeH9woq|(+#l4lr`u5QAAud'
    'EKlr2?hEncG`GvXtzX){5~|l>%$*L$@{)#KTj|5ss;-GxCjWM|nI~P+<Dc|%jNQT|wjUsaqJXa~CS@45r+FNc%`KVMjkm99=zRxwrTsh48O0uJr1$``SA6;$'
    'U<a&$wBC2Z@cWZuyTQa7JnH5hmH=N8N>h76Sv`D?K)u*VCk}cda{xZX67L}|suG*)*w9NiG>*ax512&zs@v1|m-AvzGl+kwD{8m99#*P#AuRb&paTs~&prJQ'
    'tGjMC#p8NB0VxztXOD3!ekD=AItPiohpf(`_aWm9800OZJgXJR-^Bz&AhE`A?;@K6-On}=3gr|H8p8z|M0(K~NYCfdzi7Ds0*RIxFOqkG^}-K<<SqK=(h!th'
    'V2zSc_4*M!8D;E~L&|^&h6N4>gim@4U8Nexy&^(S!E7FH-uskw|IuuA4`01G{^N@vjf(Mgqve}MccDDW0sk-Wy|1w^buCF`LtmoTm3)V#mttAo>t@`J{;}13'
    'bn@%-*94z~fqL_+ckf^$pnBxnX569z5&6!+j#^A$!%R?TeIuD$2EE$|eIBqr{JZ%m0nTS3CE+7U(h)&@^!_0yQ)I3vQx<?(Mw=D+A9AUX>gLhbZhh+^Y;8&U'
    'usH865>5nz>JqBz14s(AgD-&n0OHN6s~)$E70s_^*YJE!nI#6&X}D*B%;2avK;mXXkO7!ha(K<fbf;qIz!4ohtgeqxoMRGbsE@+M@q8F82AQjy-drcHxrK?%'
    'X7CMGQ?r`unzUSL8a3hsc|w}y;hZLaAg069$>5f&lM$0|?H<;L(>O-e6gu0^`D?o*VTaxS0sTjF`yXB0K?r7ff??>m1qkkQJErps?>)S*t_Xt!6V_E(tmucW'
    'grZL+?d<>l?T}E-y4SEDyOJizoNMQ?9eJFv?l_Ue59(;U>T%o;CK#-Oyl<rwM?d@!ZS6R$4;BR4<BeHcMu~r`=q*r*{a4aK&RGMmze%x5KUsKhMz9Xp6><%&'
    '7^m|J>+CC?xZ_7|%X!PeA7L)HATS8|Zzb#=VfB&S%jOk|MGHBhA&-_)FWVJzJgEdz02NqaqktK<f=PZV7<Cj?SiM;(0)|q<3?s5wQjAr3=$us$GKUtR40cB5'
    'E&#qm&UMlkT4X5MDsmL_)*a&-i3sF8y{yC1uIOV@DFUDgaA1M{wU##|N6=}gG|bKYoDXd!5aX6V!)1q)&oh6+DA5QNz^Mf9bc5$L6XtZM?$R5rgf%!nQ>s1g'
    '4;^#XoY4lL_*di=?D~s%f(kvZXr3UwzyFb0=lAC)QFF7|ir!*whZntfks$eD<~F+GYQRPBY<F+q{iuhIr}x|mkQAW$w=cX~1EG5eg`d@MxAdoLv*6FjqA18c'
    '`XQ>0%x1F69=^s)>!J1Rh@R9u2Npt((cUn&C<0%h0|UE$sGRGOwmR_M#?=kwGs-7S5IIvmBM;jBsKI|cj(%)D)Un0dZyIwMK?9WWXh8wSZn`5@`EbgkL`UG{'
    '`y`o@=s%tIqT_7tc3C#0==)kxCM0{FWY2`4K?)+W_m;(R;~<=sxAA$@VyJu(Q62b_YL8@m`1R@YXBV~`W8yL1TJllQ-%`3`VL_Q9gzTlP(W;W~fNfy%lCOYt'
    '+cZaFJghT&m-YJRcq#0Gy!TE_=>6W9tS`*I67xaWm%Z7o2_X?q!OvZ@XMAl@a0(}BimWV6k(Z`vkE1-)O|RlSxMAAr8t!6QY#KJiCC`1A@^gmC6lYiU0TJW#'
    '9LBk~wN&gJp1tt|Aw~)hBQ6W<7J4&fAkWgW2nVQu%OyFU!v&~t7SaPnyui3{a|iKt@zL@%GW#IpYDDO+aBxxULfxTJ>PJ?ZMrTXWjqrhCBjXS(9_B4b)sPk+'
    'aohH03ojam3Z;m6M@{q1M%~6Q;Mh?lIh{8%8^}-YMINn2#SYQts?V~JgC7CVU~BN7X0#ExWZ1X8@jB@>!*0<uF)EIJ?(H475`RGafx8Fsnc9Zr5r7Rlb$-#f'
    '5iqB4&8*lKMsy|*w;Rf_C9y20SHscZ2NGr@z5}D05Nra#L*k6$<~eBrLE?P+{1?mH{euNHI~>={21~r1m6&OT(-g-c@L_u#A+QzND+{%1Pz_9d&UxNW3d$eY'
    'voBScKLx<ezMkVy+a$`QhU`JpdrDZb{NqczQz)T`qc4Fhy~WVSU>B5YCvG^9EZS9A3Y;iw7s@k#N7=4UW{UZfPjYBmbdKTv(kHUTo0{h-{v6nrykVSOsqi4V'
    '{UGj3Knoi&VP~gN0=6S+EWewrPJB-cx{m=;%%{6!ZRG}UGw7n6w%LUKDC^CXlbHblu^GnoQB4@m9+7<3Mc|LFX{gr@`jm^pA0Z5X<l*o~2*e-xNc<5&@khm2'
    '{80%Qzcm{^*LDX;l-!nF3WyREjofPf*Z;%5aa|=OSyJNHk%_iYCOXb~gWLKEfsvh{6W77u8VCofBLCm$=NS+LRNv#zTDLd2=FH_uM1P;D*Iz+mI(V8FnCan*'
    'qoZHp(YE~j`S|E%L=Zai;LQ>I1erqBaeVaV@W~rZl+;I5ugU;`&wk>1?MElS{q*Me;K`fr)5D+MoVZnRP7wl$c5?lw6hGv(7U_gQIt7q&dUKKhVTG<}h|{a{'
    '4&V=!u#J8w88L}y2~<fV!qMtbGS~ki=}oB|N(DH_)=vsOW$(9!PMh?;M6$3Xw6(3G<;*tR7rt~qlARd5ioR(6gEbDaQ<7a|axH1Gih&C3e9U$k=jCksL6^Q&'
    'HXG%gFL;rJoRmY|o1C55nV=(cDmPrr?uFvhH}D%bT3zj&Ko)YcTbJ%&-+rwV>maP=b`fMA2BOh`G(NZ*-y~r7w&5q;cxQe3Lz-kn`M)IWJdNn+JHQnq{a=QW'
    '{xK{#PmZv7J>|9MK(9o@9WeTTBQ5|)Cp0%)XYE9}P#FU*RZpk0iKJsmd7fza(i25gabEPCDkMMi)SW~+|7I(xeTHo_c<d$nbeP`+REWh?I;U?^(=Rt8H5Ln='
    '4UNxw*KA`LI;pZkfQaXSpE{T%IZvP{nAo)xA2ftvGnagME^v1tU`#NBMG;af?N@1loizv!lYTop3C{46EuG)a!NkX$BO2FZDgICNeVMLAcF~X|N|>8IZqQun'
    'ag)SauU=nGh{Owjwo{=g-BSSaC{pm_jXeqbVk&t$nQ#|M@}zwlF4$EC_jbY_E4XDpCy|>uEefPgiyAr6RaGy;#|8tL%}CfFpy7ZT1%qVezRROH$5Gwc2I{%1'
    'WT7hdQOlCA|9pst4z0Jf+N3zDt7xAZk_(Tp_1IA_NDr_PI|+sDlfDs|{A$=rGngO5ORl2nk41d~VVDb~M6?Dd{_r%EBp^Z07rYbDlR4q?vD!B_2^O?-C>_U$'
    'SG$qYk3DIk&Ocpozi9r=>}Z5le1Ityc+vR>&ePb}?F3WdX)tqZ3HU@nH$9h0d>lOg4t=L-K{_laNZl^Pi7UrH+om0<>&{|g_}1Ht20Aarz)whFCe32B+f~hC'
    '8_ZY#wdB&n*EFVLU4poDF<sbDSAffpD`}||Mtr?%ig=YmfN@0^Y*tq>r^v7dmk2YOBR!ocdRlO9%kDyTPvM9O3;#<9fVdxGzZB;5a8Oult*}}*O9J8=tl9%<'
    'JvN{|#iP<NOgwn1Lp_3iceEob@>Nu1gT}KV&T7Uh5qlyRd=Sal-mI1wNLCr^rChL90hOm^>29_i6z>S9YsC0<HBam7(Y#qvnd0s$O8?JQfjJ^_f&R<;oHnx2'
    'o%ppmw5_DZAP#kL6tCZxoS31YrqRIB<<{VA7nP!|Lkm(A7~JxM-rG*q9i8W4xsuSoOIA@5;z8@5_qG~c@~G|J#kX_WH*}(Njkuag)AyWKGWX@z)KEUy+&XAQ'
    'Z&ZZrk9FMU(Lb}<r2e)COBTHtUS6U5E^fuzo9>&#<Ch$6@#65{_$z27-#pkl$g3sksjI)ksNODROh?i}zl7`<reN`4t9MtJa;qbMB2f8{O@_gdet3{F>h|E2'
    'oxbUFc+Ikv+n_>&v=mUfpXVf1VF~FR#=8Ux+LD`FyH*ow97vJo0=0Y_{Y=m~BaFlz*Z&QhOyC+PlfgWnrV2q|X@!v$5b;jS4TK;eMsanMT@s9bI1M%5XDFov'
    'P=oBo0y?K}qZ0%aKfRSiZ-Z>!S1!jn^^aZGCJLvu73I%RyFZ~FSMffQmSMhtZz(!b)E0~L3^@6~B)V*GQJN)UoSbgATg^tNz{8R23y3bPx4>nAwd%x0**EQ@'
    '+^(8q%VgWBB9M-$&v%KH>%oS5T+$8^i|UH*iU!8`tK1>0k)~B{5^J2RT_yK^k-UEX`mp&RdUks{8xD?OUl1q(o)`jkpiW>W-a(c+Wxm4gfnDjoJbH?5d)33<'
    'Y;^nNwm-_M>ecbVTVgV8)X|_dq|s@&9zDQ4$R9q@_s$cz1P^|Caj0K8u7li)x~M)GxccdEnsteg10#!bp*942YDTJB<DZlkbj*~XE~egS)Hvn%sCqfFQ4Piz'
    'K4@9es=~0SDoMyM;H;dj<fM+kbQuIz_5$)B#~baoL4i(Gn%1Ur$?_6o>VDfncloxYPMx(?RlD0sN?X&lHJ#clfiw43`+nqORT)Um?FbRZ*uoc*KExX33gi&J'
    '1c!rBMy?Sc@!#}DALbMt6V-N;ofxCCFiL|hHBoH~p8;{gUz;|%K{ibkdMEVe(^jipeT$fAon+hmxnus^g+E`vICy0yt&=>!*RY$9tDVn*w1F6}1*e*31{>^X'
    '*FPFy-kYkRr1VqG!x2aMP%dNgw2$zdWW51Km60ct%JvD<U%$;3^>LP=TFjjWyLVfUtQNPZZ?0#qeTw|TdJgP`!dM@(PK_4#G*R%U2`Lva+DJMDOj?G4MGBxm'
    'smpQ4$_fPk;FjSpg=xnd+37nxIXsY8`j4l_N3S&qYG_ORdpMP}T04)D-G{MyH(zmy8!InyBfrEi-|~%sA-Nf9BcrV!cea!0>BSJ(nPK$H=<45t$#smG+GwK_'
    '#9M}$TzYWN-JEAVyiT+$C945p+fW|Hu|}a?oX@h%-aoi*I03R67&}J1_M_&eL*n=dTUSQnkvtzAj%v|X+TCrOQs4Fyo}2t6PA+b6U*s3{p0>mCE%9(Cd9)QL'
    '(2-oKqt$i<Dot>ev0QX9oKujfp6%}j)#y9+s9kA_ob6*Sp*Iwr@|;)q=<Lblrt~H<T&i^wC@7?+&0zK?Hz`?CmR$goc1w{H4c46ygs7vn=Q)E~iTG^osXv=G'
    'S_x(*X4`JRH=7L+1Z6P<X=idX=HS}X$<@1as%DRVPvBpO(R_m#_&}cR%1$$wGYMCeC_-}oOb9J1Lf31-cxK;`QFgWv`%6FD3=@DYYf*MOYUE<nlTnAi+;+Y!'
    'B)|S=JK+WiE;iR*po>NHX?vwoJGoMFJ<68x%kTQ-oohqJg*IJe7<#U}+*U}8J-yY4-`r1|4VPym{}Lj1O8h6o%h>XU93wnpVW!gno<qRikr<0FwwUJZiYlRC'
    '9!*h}$$$-X;>5BfqILs?c-v4$Qs!1?BUNg?k*b$*I`^9mMnaeeu`9HRjF`sNoKZ#Nu7N-mv#xbbL1D?P!&*`vA`>PBdLT>tnndOJi5$`aLY@&ceEh^B>_m2z'
    'ViXe&OfkEc?mJa0N=uefH7}=lh>C7^7=uw9j!m=-eh7c#e=PRhmX2Ik+T2^QEFcgb`EX457EZCo#4rY33<B*EetRSLSa<@85-v@dEUeq0E4-VoP?!dILkF-+'
    'YzVbP6jqfhtz3!{yQqSV=T;rk%g`%QjQ9nX4+jCT#&g(Bc3`xt+_ZN7y2?%2JhHcFp<VxYD)0@+-$te^id8n--c4ttu^7ElI<t+Z#~dy)KjsLj`Bq-l$43$q'
    '83$BG)&@kCQErb_m1W;j$zt2K_dot-!it|M?|+v33VXA=vu=0v-qwB6phb2X9~8H^HzEM%;ic_v>@Mv_@TjaeFIH59Vh0Mkge>{)j|uSV1_05GI3tB_81vVT'
    'UNf8}wOiXsqMg{%v)k@Zlo-Afi=kRE(goVk@fS{hKA&j8oge8s#zl%%XPttSi`FS0^UWt3mZO}#b_rVOyzMNH=BIC+Xc>BvJ2Ap?<%$S02!_O0gXZai(_`p0'
    'O+o<-z?vb7l=qp6_G9B17u-@g>;<i7UK(*pt?-+vmDoCz`y_|=ukb<86>3zoCsJNXo;~!2Vk~-+3wTr8#T}sf;(csVrQpEaR4G<GV)6BbK$-C2H~NsO3f(}*'
    'R_O&86(`}zMO|@56g=(XLQ<>#OoAc>5>N>DlcN_e4xhZ~{(N}+=J|`~{{$W%o+^PHk0$Z`NyPi&UOGn!V|a;{RA&!^V#P!X*|SzZkK?h@adCN;YNrH1Lo@N#'
    'E_z%FlM(E@)^gmTw>~4aw7-Ql74ThLp&4L#&CYRZl+D^aTX&j5QLDMDWZg)-JPZjtQakq>BO)?QP@0r5IhgmM=+%h!ALb#@Ud`oVsPehXdyciX<VF^gqZZ2x'
    '4TYumsqVdaUGs43rr+@jaca))@%e6N13I#pg8=Y#?29YOtgF};ts$=Js`6E=j4z)bA0HjpUp)WyFnaO=4#4xDpC2AawbSgpcRj={H6GpWAqLhg>!Xy9UP-g8'
    'cQOA8cE*>!H%fnmR=TqxLsDG~aRYQm!w(t#q`lo80DI%(k3dDreyE^FCo@`5w-ySTlMkN1dIbY7oc%A_KI^!ySdxQH==GSC5Wj3p_J^+cf5%z%I%f+At}N?x'
    'm&D7-ObauP<Y}T66o-F{Kg4imgRT}+3wMmcpjNBbTcy3GuHx~`^*#?gPDO3)Tfh;dM_x8uwEhLd56r5yY&5sj7RqhA;m<S@s9yXcmfbGxx57E4RZH=bkIh!n'
    'UA(U)RRmcb+~pWg!wWK%^)V|+pJjvIJnCNby4ItmblWYy`Q*Ge9KY;MYo@!2>6H02UWLfxcM4zg&+###orYlT^`D;~pS+1`?|?oG;ueN^oedWRb2{w}XLEA)'
    '##N}}R)|y%kNdv@-u|@h-2t<Vl*>r0VkuBUs_Fgf0~ifzPivK*j(>ag<XQLR_0gM35;;H7Bf0X^!LNtMe*|B>e*VvY!f|_c^cr8EygWL3^X&N{KZrly!>wT0'
    'DLtsQeIhBlZYpY-+~rcijM5cy8nm-YSKO@9j4z0spmm^mxs{A-ZXf#IA`2CpOJ%@9j4qeYRpuHJTFu&U7=wOs_jUU0`g?Nw9wk{ZM5V&zDqf&oFk1<Qkpu|7'
    '#GtGfH&U@YTq;idScT4KC9MCUwycaK4JYEHK=xTJ1jGti$<cRnKoLt(j%KAyC=82EVmP8va12TOCEkOD^!?^^n<(~D%B~7pG~J9fvCinaR2@GoCF@^_wg36W'
    '(c9O*BQVW%7NMj$s#6B4QPvyO$#z(S9%QrL$mQ>Kf+k=Vd&uQuWykovl{jI>5QGXYjaGx)tEN|{qhVj~D#h2J(Pz<{CknY22~#wf^=^2>U(G1x;QZ=TAbZKH'
    '6i5W(TK8td#W_qkRErT9n8=B6fZw8viquErBM_$3EE_8vFqDSJ67Yy_DjLN5EW4pT^9jPoSg1OWF0UpFs&I}vOZ1MJNrEZ-4WjOloP&E%8?0ZV67@-c39lPI'
    'q84d76cjLxnHxlJrmGQ(@RA&bv7#2|Lq?DSy5CdzS;&!_WoXq=X%Q=w^fI@IH{Kf}Iyg=wNN1zrzu~)Ck5hJL<H0+eN6K|I>!HuN%5~Kn69BSW^7?$5^)X8t'
    't^MZxU++KvZU9Is3@L&%U65w+n$@5r_>0g-@Q=e^excvbU;K*yMX(aY-NgEEn|I$ne}&MI#&Lt@x+U8JVP}U#sPx7-LprQKe+i#U4o>G;8a;aS$W+RT?D=G*'
    'bLVjVf&_mv91q}p;abjy@7|$X6dg9M^u^)9)9y25xwj&(pSW+_jpS|+uHb+FcJ$^@Myl$tDxjSk!6u^PMggmY<~<^CjXFy0<97=<suZq=6~YJ!?hS|eK=%kS'
    'yrbTYfQeHj^Zsl&CFF3n7xU+ihc5hf*|xKf-7|zLrwFx=CUy<}rb*M*V0d5&nc6!5zhQCJVTlYhpyHw`m5Sh@%4#r?QWJn-P{YX;A1yv<7#)R_u-e&#k5v>s'
    'LEK5iRRw=m;xge~qu07{4p<E(InAzB2~@i)B*T`UwotwvdqE~`#f@~@6-`4GBS2&m@wXp!k&JfncTHL(ey)=^9f<Sc{rVuffs6bVM^RKdZanfn@GX8u)|}3r'
    '&IZoawS+a-rA})Q@@9j^;kKblBiGs~4&bL&@_KMs*9xvHG*Pq1&vDx^=?CFUPtMdk7e2Q4X2sJWAp2%oKn`%XxfMb~6X*o1EU?zQ4?2at^<W6?BTyLaXrF+U'
    'HmH&mm<P6tk&FQQ%o7SaaUNeHv^~{s(Ri#CqC^NqP9BIzA%?A7=nzK^(VlcR<mcRktLkvdA3azy<GOIWwev7E<*Gmc`%xp$Mh<mUu0I$@)@ZZ}6OSs$n-Wo}'
    '{NpbZRD1y?jb0x7-aR^gdU$+N-fnL+Lol^<gXghZ6|@?VRA$LA@#nQMW7Nh{!sH5AQ@QP~@%W4Izbp)|3b|{-6siPCfuNA`Nh6Qk0@P-1s4a~sGcsPybj6rW'
    'sDzn*rXsk>Ud@*m_KUtz`?4OnYyePXgfyd5CMzjOFBU%T3RGXcR{OwBGFG^g!Z!ek7;Kxmq{ay#Bv$c-hUiHkL{MhLPALEtiG<eU*ZiI}eD`{wF6=wp-O_Gf'
    '8k1ZOipHt@a<z*PZV_5bTtJ2Xrms1@yw1uK@=2gHTy(B07}brla*4x-iN*(U^aHIL{k^n%irdVC$Qb8)fk0~}kwUA*Js&3u8_i;B5kSpv)X*;S!(DV74U|j6'
    '%JPc`6edJ;a!5M`Di1Z(jZ$#4%f+oA-4p-|X;IJH4)EQ6-d`p^;}YRH9Haj-_M)w5r+|hnZf*6O$CeN)ozt>-g^0)ILQtEJc4PZ1ICwXuWR5eYyULr`eq~qz'
    '9X8r-8G6wv$iI#t|NrPdJNoUI6V>b{QS$-(^CSH8FrnN<TbxSZA0#wA<Uehh!{FIpuf`_<vwwI^0!&>*wf_0l7!iE5N~Fc<ORuIV#hv#?XDS63rSsv=Fc^se'
    'gLA}x;5#pdR~H=ls|5Qj>R-)fs8XR>;M{unm}R!1C>n%@7it@fw6dy5au4iGO`}Je%Tle}|6T0Nx{UDO%uk;A(Rza=qcF$^idV9b5BS#nujiEhlPt%7AG1NE'
    '_rIUd7#dCAN^HXld<nJ&^H$rAzBiqSwkc`aPW<PyD{vhvb|tl5@OtQ%E|^!K4#mv`>)@AC$A1H}14AeeiTXlYvX2Apnt_F`TBN1KBZ;{Pr)-XL`#{eIo!E_('
    'QY=Z!htg8DsU$ggTXR{Cbz&(I^8&%&as|jQ(#^K0vCnz5pAfd1**~IEzN2zl>5xRPYr7k|X89Gg*UP;iUFJTJ*v<G4=-suh{{Y&6(iJp~_t0C@oWn_kx)WyT'
    ';pKhx#RrzUGpk0Oz8PB>$L^H`eGW3Yd2H56(bZ$!PJx>T8rS&8@b?<n$GDN{C^=`3^O{)d`W6$z<+h2qFnmsN#^qHh_8D$8(*L(`JjHdglDf5yKKt`M?P6!<'
    '3^2HmeOU5RhXkm1C4U4dXSpNj&L!4~U)LJ}K3w9AaPN)?PY>R{LPvx_?`B*mc}F!w&fAK<eYh8iTLPut&3Pl-vqk#pYompLlY+@|V|grU2l&%9Z4Rd9_JF_j'
    '?E!y>ESd1Q7__o=CxQOagZmKU)zJSI<Np@p{}$u_7UTa6F`nq^-(vh<RgBknUAv-gxxCfEE%bG)4u#m>0jXOhtA>7kRT+C7nYk#6N6(!SMOR}cTyakibX{>z'
    'MNO2lB+I#EcLNk~$*a5QLLDn{#8S@Uh;>I2Yf{$bh~dK}9C7!h#UwV7ON4{k+=73$V|gpQ;!B@bys(z{!dl*oFt2#=SLGF7{>>}?%`5)REB?(Z{)xQe%fETW'
    'zcR1*(r^J6g}kC$=&!>ozWguX6<_+i;%dx<%PYS8QeN@m%Xme11AH;Bc(Ed{c#-23Us}B4%e(T5FJJ%Z+Ed_5o<4uw!l1nR;ykMlhEpPdBaC$v2w#e#tNod3'
    ')1RKwWf|!pMSjLXGY|QP3RU4>PY(~CzIgr$y|*6llP3oldh%e0e>veK@Z061Pl1`5j)nvi2!BsGQG_`H@N5Q4*_$({0sIWH*YNnh+3T$xo4tPUsG-v9u8?3P'
    'K+THmxE7;i8)enJ*_q{(k?~Unulq_1E<v=K@{GYxn4Svst)D3)s_p16EiW_D*cYza3ob?D+T0)wG@MYMG=^}E?M+nJySJ44KYxI1%FaXY4jW`6tIl?7OF^aG'
    'T@JC9x2@-_<BdbHU3?I0a~MFZyqmc%Hd`tu0qx-~L(1taF+plA$YsTv8Kb0vG)Y!g!K+NX$$2q5f%H+-0lUa!-ZSbfdci-kV)QZdsMu@lA`BDS^Z76gw@jTx'
    'v#ZB8YYO70pDhi$-jABxJsc=BA7IQ3`{XQP5<QHI^0;U;T&KH9WOla4`#6?By-DgGSEKJhP0iXBi%tdjpy1xy55w`<%c{(f1-o}Y5_0=j+rz~PftT^=%lDPa'
    'SH$R8vhnkw0Jd00MT7E!dp6WB7<hqXaL#dXlsOgS{t~qUavrU1d5KK>Rsr%K%533aH^&Kpv!h~5=eYp4;{6J{ue`WyB#XWj0NoVtOXDFEL=$jN2Ho(LWdL*D'
    'M-D6Ck7}uKpyYv{o_<|<pdc%xB@5)(e?3ga{(lh<WLL{9g98<91O`15cNG{)nXKgkgS)z4EHFSFD+vrz&Jq}OM-ppN))g4w!#`VKK<M!o=x>1tw4?ed?g#R-'
    'peO}kE|KbDB>fL2*j@_{Ujx<cwH@@YLipW4e;v?|g_WwEL2X!BgxdD4?N}A@mFypF!T6&s89NSqT>bNtH+~2Smcwvl{!&ye6j|0%xls&aMZY)5fWEaPrZ&6I'
    'U<>U~akxfN*9Mc!Pq%iQknM&mJ$wgWd8eKV=8?-#8NZ~cB6aZ88`yn|Jk1?X=6S$yJ|U~Y@2i*%Ru+0RUmp}tbS!<Bao2>oBRXpw)dUI2Q}EkmMaXdqDrL6X'
    'KtX{^NmAbmn2Lg*;Qiv@qxirm4hjJ_md7E$fsHA+QpHotP{RS$`q+K8WHP9p85j$mAPvG31S;~SFAns_KDCEVq(8>^V}O6|SS7lpV649z=&z>Tp6Ve%RVjX5'
    'l&*s~EHsd|dq|?A6RB^Dk5Z=HdSF>C${iysEj4WIsrc#hXU9rnoB{;{Ptttc(J<z*$x>S@CoZp|(Jot2d+f3>+PO6F&UZHTSm-52xvro3B$t|<yZ(7)3z_ef'
    '{+F_beSvXsnc*t5oXad%GW!hmzuY#^yY3A~LZAZ{38!5yyOPOaDg<pMn-~|~&!;BH*UNO*BBTTW!iUN$)wQHodeE-#v^q+LwVse9%N3I-+t_S`>|GDa@I@Kt'
    'B}cmR!{y28U*V;AHk$MnweD>D$F8g$O_h8G73IhuQYVa8CHjo$YI>j>x~KIrrpNDy)K=aT%LJx+5IYHYmmq%Tmys78+uoPisKd1H=JLUP$VAqrt*6anYN#Y%'
    '=dTF*u0XjGMw54rPO+g3EB5sW7T1b~kfMn0U{Oo5#j2OnYzEjVrrFx`yAi1HtJ>mZ?kE+qF~$A<my^BC5*XXtiZX^%2eFC;g0>m=-A!{JztA@4ZnS%_&V5|f'
    'JohngpZnc5(EWaA3*Da|;BfNn`QeMFbrfw|(b*NSFlQ=qe>}YCjeZy*TSG=Vgi|LTXgK;%NBI%+2aYhs_<f7rCod(FB5|=#j@|;Fy3;`8&&jjH!`JX@mwx?n'
    'baZkEzqT8V&-~eogI7=4(+vx3(ZAtK5}@HV4wF!DNuGC6a-Tmr>^?a@Ja}1zo6A**=2kQU3gpkj{<E?E3<RKo3N-M6Y=MM7OfC`ClB+0~UjWyI86@c7&M(X%'
    'hQC7wLwLMYdKU6{H+!E0%T<8iTZ-MQL<N^rk8f)Xx$CSKB`YN*KYseP(WtN^IlX>p3ebYRT=oy-H>*&7vx?+5Qxi(J7cF-n5SBA;cvFhs=trw~{uS#9F0Xn6'
    'T2D!;<*gaMp7q8Hf8F}M`MGAW%y$=Xi`{aVGnCdLsBBzNO%@wbWDzE-Fj{Lx9+GI0l0aF=i{(6`_-~wRm+M872#lzV6;|9@*bG9GC(Kdwy-Z@cIAP-zYIZ5t'
    'iyVJMxp*8K6qDFx^F=+Zr;#Dbmh23qHHL1Nc#!3r#jLxlHu_2EV=F?}WkohyK-djA#mm5@z*xGWAy`|{!^UT;&&@mZ*)i8G?{;n(m8N0shVeeDc&%`z>r~Eb'
    '-RHsW1;fwVRGv(t4U`%9^ZjU>WkI|hMNN?r`Ke<Ch7x9Z-@gDM?8C$ik=Z0gQ70hjTUVzIi!F{Dt89EnkYDL227LrrQNxwx52YE1_Vb_*m4HOw#j!u?O~i4m'
    '%}{eb&r*~>JOzk7C;19-hD>E18B{Ca`|obhFKQsH3pt%-y$`MjuO(^XG*aC^hz|?-tL9yKSJ1Fv7mOo<>v?HQlhho#8ldl|Yfd)|PrIU+8}Tw&SCaFp60XU`'
    'L>+v@#D|p8c*y%S;fu&*r&H6c1Kj6}Sq%?oya~M0Y%xb5>KdNX3SJP_%J>?8<;w}JqH3A9#D;ndPg|Xp{Xs3^6HnA%O!m|>uhaFe$hErSr5@Q`rOQ&@ce!xs'
    'ZlEs~EuoH;Bugo036{Dei8U$fik0x;N>XL?^G+*zLFTNdKuxocFtq42n=k6KY(9m-WSsIFg~M9+$?s3uDwK^T-K_`BU4B_VolO2uZ&%jawh@H?3ei4LZ0JBz'
    'oivfF0zF(s4@p`(0SXWTEladaSQ1qob`m51y*tOAT#A$(_o0nRE%)A;Z+5PmC?G+O=R;6}^|mPHG#iso(=>;Ei5k*3@6Ri?FaG@J@SjtZ=fXEbO1&r%g#4Qz'
    'iF^Wn2f1VM<KI61F*t?VUjc`s`p(|JC0!;yDhca8gkDi}JhU>z=b2arcziBjWMB<s6u8_?#feC-AqS>@%PD`vi?7@cs<qFV3*Z}CNw)0fAC%+<m1u6j8PLUv'
    'nHO952jca`!BzeV(%q==fbV%}FqGc~7P_F!0T=k;1%Glxe2_I5SNR-;eTuif*>XJioN^jqAsxC8d6&vg3QV2W^7$%TFLqlzWt$dv6Kx=&7nTbIMM)v4Oy*s8'
    '6MW=afroWbNLAK%sP;#WzAvWULYXi5O6L~k33KiLL`Oi;*Qc-c*99GOCcLg1%=M__X{cr8v?D;5Tv=SP3r`Y6>;AuFSJ>Up56cQXI|XkM2QBy|CaVQO))5$%'
    '@~m+4m&I;&y)CQ8v`(zBV6vkb3k^IS%4o~wosDNA=Kl;hSz^<?jUFR9!cJDy#*MoTU6a@*k4~s}@<mYv-YF%ee;ztI+YL@-U5hv^Zi_rf4&F(?5Wj4&Ay(t{'
    'c(K7S{Kv<iQ+k9g8QJ>2`<tFAt=zJX{w5A?@hH}-1EWaBO8%-00oq(MRcX~IzNpA7=TuXsp-FG#z3(x0r8KYx(;_?$3oN!!>(68w5@4g1ctRg*!|Yj3QLbs;'
    't}y><O7B~w&ys0FW1i$lH$m+xJ8d8d{3+0S&y5yf^(*=jYq{d12)*Ey0s|??b48SstFs6z{G?U*TDhOG5p7$atqGZ(K7{}9j>H=JObj=*=a2eeqbgAgz5XRI'
    'n7A7iO*8ML#E5-*DMu0#4WI?OIsdL3;SOX)oY-d`#oZ;c1bcGvqZlW_*rjGS2|r*5@lSP>&5FvVsy-RVt(vflIrdT!gfmzIhjoOzr&jPVx@O!iLwyfS7$;%h'
    'q1e7c95IrRdIRX`Sx`Ad<#d4<A}6MgC{Hbt{K?o@@|8zl)}U*@@W=syI$e}Pi-QjyAh(qETV?Xe22u-B0TNr}V%y@1EMUkhx&yIZXiHuxA$>sqvi_#&gr&Ul'
    'q8FV0^Ve~w9b5?sBZt&c>tMEnyi_encieduTx8;B`u0MKCFv==bJQz0`HGg9a)aTYn9Isd(2E~85xjNFhaVE7k%RLp`Yj?k(KO--uhJqUr3Dt5jz6;jJX#<e'
    'H;PrMa+;X)+q0gMo008TO=+nFOEp0+r6y<4%c;%b;slwySrAi}hqgMxQ6)_%L%7neg@jnaijf+RdOrFpwKnMA1!@;ed@aPwcc*9RyYnPWCv&lIDJJm_NA^Ub'
    'YA0mXP8`^iOx0N_a<xn)x(XjBatidY=`{@)R!Ho-<;*p$sy8+>)lEcARtVt&as$T;MRRV^W|82>7?<|8+j*T*8>!eOE&4Nt9TQoy9A_&Ny9oU3&R%rV;k&;+'
    'ejo$>b8G|pqC+QycZFa$YiLuvib^8cWHGgoKc%YgL7&wOMy2?a;wNQ~t%`wZ<w>xGSoZyZrWPJx(L@<A8^nLxqjDxq=tgNvA#&0Z71YHlRLXrPo@tB|NGOcX'
    'N-fTn90wt(HNr?b=-gsrc!_><>{d>SJKgG8C?g<v)Ji)6wd7T~Zd?(`X^I740YxoGod`A*=S1xD$AV!26?hhO1;r4=5ojG1@p>7dFapJJDoD@3TZ`VX$RjsK'
    'g(uE!z9E7j0BA}N{=lwcc_{e8Pmpt=B?pRBYzZ<6jBNyW+Al%r(mlrD4CD2-FJm`UxGmk>NtW=r-PhHkKu@=qAq4!m6Kk}lX8JHspypE(Eq~k=&<mEQAvEx^'
    'xJ#k^zQ<HeT`8c36vj_&uEyJI?gZ|hQ5;l_Hs<+@kss0`_woO6@WT%`cTv)=$c?(p?!IZGKuow{-bGPe7kHDg%NWVZb3ALJbKX4%UsUWPq78U6g9lde5tDLi'
    'GqIANmdUe1#0HF_PMqKPOoT`pWLi;J?vT)fR~)f93EouW)=Fu23w~npo|wsBtW@)gTtzs)vDn|F*tEql8fni9?}@|oX`<R<eUaevbEh|I05`3Pcofz|s6=2>'
    'qb3_|sv-v5G&&Gln5h<W>Q)ZLoG%G;w!6U`V8I4dT4Je9z}fDW0jGGk4>MAU-+%r6jfx|HZ)}h{*=-F4%J?<|0KP$|I$mon*!WC>uxsmVA?7b%&J^!9orTcy'
    '8+2o22_E7z9GjaAmZ62umZ`1SXz&~1J~;@r=ZtrWC^oWG&Bo<}H@MDEo!2Hi-)FhrMGA~QJ;$%;1mZ8IukQqwm&5KjO37!G_N$}8At2IbaCAQw^*DD-^ljio'
    '-WLKz_z?0t@^$ba1g_VeRMcf=w%;hd(6Wf!ln;?b)aL#FWszo4^7VY!7OOtdM4hUh^;8l~wA0wj?s27%u<zDBu9QluJYKYV%kp~hVMRCgKxGdP69^P_AeviE'
    'FZ3th2Y>If9VBfQ1XrL{xB&yz2PW@kWzssI<x5C#JGsuLyLom3+8(jonM`)O2)0G>+}985X#NW=!KfvDVo&05^c=6>HmyjisbV_E_{AQ#?{9S`pH7-ZdyVlW'
    '$}0CO>q_1)T8i@}4!_{V<XWW6W5g^@l3sU2@(YblfQ*tv%u`q~-mk7UFB$C-M;{y}q2eg0$?yQb72EZl$UqvdrPT>#i00r1+t14JL+`dD-9oa$Pt0f7j8KIa'
    'j$++EL)#Ugbb`|beLKR!jj^aEQlWwXgtWxtiBm%30#!r^K&?(2ji7L9X-$bscH7m=ic0gs_x8nRz>8foc`T5Xs3tsv8TF-ysjWAw@j4Syh`=t;d$ok@3T6M!'
    'X_v+Lsw64coCShgaR^|>M{1pL?8&I4&Gl*a3@Gj6J8Ef62<FB8il_Q6+Kb(`5#}~pd?e-;HA&1Z(SeJ(xrl|iRR>}V8#KV&vXuid_uJF6fk2d-@gh4ydqPmI'
    'it#K~JfSTdU~v_6U%q}3Zi3Sve>_&$`|ZGWxu0p2EdCb6c}BOq;=yvbA2hn=O~q$VYiR#XL(|r3harEEVWKT*JX<{a==@$Q?!vX1Z4kpYHY|lp`DUOyEjrae'
    '?91lXIm!|+3}4cj-8O-rl6*TFQS2Gy56)|kPq0PFYv{J$2TwM@Hui-@xIDCnH%*!L_!NR_n<wAN4Q`pNIR$9fQwei>964RvqZy<^@)*D=cxunKf$P}T>?AwB'
    'YlFwSuFW3jxn`}y<NelVOvL2^INoZrlC#>t@KqZ$CEl|314;LA5VS6L%jq0!1sJ_w7xV0BGA}l}btZ}Qa3J8rIfNp=S{GlkB`6JAhMSajopL;_qyrYaSXrJ|'
    '7;<H3kpKJdum`EdsX46Rmuy{#SET9YcaTuG;vE`8@GD+JHuxJhWE=SmbV!>l#Xdbf^Qh(&591Tc{73TDgTezS@}kAfdkj}>qIOlIZR#J{o&~&jzRDVJ^NnS4'
    'Pb+I*H$nUvAHyQMKekX5g<M-X@yc&4hoNf>Ce$(w?4Z&Z>x?uvgqJ2qglA9S3w+JNFL<O;$$&s?p^et!Ntp*fwLMITIAsDeXEMl}`q~hK64|WF{5&PVpkG#5'
    ';>D`13TJg*E#*AmW4640WjGBJUtcFpv}vbT`fAS?K&(uk7CQcVGfi_^WP5w%%W3w>up-q;OK!?%uLy<Rs3y?5vIT@nquNl|#Vy|zJmnVDAqwRt1Eo#*vP<@c'
    '1IyxgYVE?d5FQvv77c$@tXgeLw~SMmP%)43tt@~OHZm5kc1n45?X9Mk_*tJ8R)8dGTM<r0bo!0lMm1APyd25GZAMv}M`0;?RW53?E-Xr~DvJ_F!;*5uwGdG5'
    'X3f^}Cx?M}m&*zVH40ZS*Tduc@wN*ChmVDU4fuCG7&MmQ(MT|tNHF&z!Mub7hXxWHHb#Q^0Z8yan6&(w'
)).decode("utf-8")
_BASE_NS = {}
exec(compile(_BASE_SRC, "base_agent.py", "exec"), _BASE_NS)
_BASE_AGENT = [_v for _v in list(_BASE_NS.values()) if callable(_v)][-1]
_SLOT_START = 288
_GUARD = True
_FIXED_PRICE = frozenset(("HIRE", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND"))
_CAP = 100
_SHED_TILES = frozenset(((4, 4), (5, 4), (4, 5), (5, 5)))
_PRODUCT_OF = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}
_STRUCT_OF = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}
_FIRST_YIELD = {"WHEAT": 2, "CARROT": 2, "TOMATO": 8, "STRAWBERRY": 10, "MELON": 10}
_SELLABLE = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")


def _g(o, k, d=None):
    try:
        v = o[k]
    except Exception:
        v = getattr(o, k, d)
    return d if v is None else v


def _slot_priority(observation, action):
    try:
        step = int(observation["step"])
    except Exception:
        step = int(getattr(observation, "step", 0) or 0)
    if step < _SLOT_START or not isinstance(action, dict):
        return action
    market = action.get("market") or []
    if not any(isinstance(o, list) and o and o[0] == "SELL" for o in market):
        return action
    head, tail = [], []
    for o in market:
        if not (isinstance(o, list) and o):
            continue
        (tail if o[0] in _FIXED_PRICE else head).append(o)
    out = dict(action)
    out["market"] = (head + tail)[:10]
    return out


def _project(obs, action):
    """Shed and carried inventories after this turn's unit actions and market orders (engine rules)."""
    me = int(_g(obs, "player", 0))
    farm = _g(obs, "farms")[me]
    priv = _g(obs, "private")
    day = int(_g(obs, "step", 0)) // 24
    shed = {k: int(v) for k, v in dict(_g(priv, "shed", {})).items() if int(v) > 0}
    invs = [{k: int(v) for k, v in dict(inv).items() if int(v) > 0} for inv in _g(priv, "inventories", [{}])]
    pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in _g(farm, "hands", [])]
    tiles = _g(farm, "tiles")
    size = len(tiles)
    done = set()
    units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
    for idx, act in enumerate(units[:len(pos)]):
        if not (isinstance(act, list) and act):
            continue
        op = act[0]
        x, y = pos[idx]
        while len(invs) <= idx:
            invs.append({})
        inv = invs[idx]
        adj = (x, y) in _SHED_TILES
        tile = tiles[y][x] if 0 <= x < size and 0 <= y < size else None
        is_dict = isinstance(tile, dict) or hasattr(tile, "keys")
        if op == "HARVEST" and is_dict and ("H", x, y) not in done:
            n = int(_g(tile, "yield_units", 0))
            if n > 0 and _g(tile, "kind") == "PLANT":
                crop = _g(tile, "crop")
                if day - int(_g(tile, "planted_day", day)) >= _FIRST_YIELD.get(crop, 99):
                    inv[crop] = inv.get(crop, 0) + n
                    done.add(("H", x, y))
            elif n > 0 and _g(tile, "animal") in _PRODUCT_OF:
                prod = _PRODUCT_OF[_g(tile, "animal")]
                inv[prod] = inv.get(prod, 0) + n
                done.add(("H", x, y))
        elif op == "COLLECT_FERTILIZER" and is_dict and _g(tile, "animal") and _g(tile, "fertilizer_available", False) \
                and ("C", x, y) not in done:
            inv["FERTILIZER"] = inv.get("FERTILIZER", 0) + 1
            done.add(("C", x, y))
        elif op == "FEED" and is_dict and _g(tile, "animal") and not _g(tile, "fed_today", False) \
                and ("F", x, y) not in done and inv.get("WHEAT", 0) > 0:
            inv["WHEAT"] -= 1
            done.add(("F", x, y))
        elif op == "FERTILIZE" and is_dict and _g(tile, "kind") == "PLANT" and inv.get("FERTILIZER", 0) > 0:
            inv["FERTILIZER"] -= 1
        elif op == "PICKUP" and adj and len(act) >= 2:
            n = min(int(act[2]) if len(act) >= 3 else 1, shed.get(act[1], 0))
            if n > 0:
                shed[act[1]] -= n
                inv[act[1]] = inv.get(act[1], 0) + n
        elif op == "DROP" and adj:
            for item, n in list(inv.items()):
                take = min(n, max(0, _CAP - sum(shed.values())))
                if take > 0:
                    shed[item] = shed.get(item, 0) + take
                del inv[item]
        elif op == "PLACE" and len(act) >= 2:
            item = act[1]
            if item in _STRUCT_OF and is_dict and _g(tile, "kind") == _STRUCT_OF[item] and not _g(tile, "animal"):
                if inv.get(item, 0) > 0:
                    inv[item] -= 1
            elif adj:
                n = min(int(act[2]) if len(act) >= 3 else 1, inv.get(item, 0), max(0, _CAP - sum(shed.values())))
                if n > 0:
                    inv[item] -= n
                    shed[item] = shed.get(item, 0) + n
    for o in (action.get("market") or [])[:10]:
        if not (isinstance(o, list) and o):
            continue
        if o[0] == "SELL" and len(o) >= 3 and o[1] in shed:
            shed[o[1]] -= min(int(o[2]), shed[o[1]])
        elif o[0] in ("BUY_PRODUCT", "BUY_ANIMAL") and len(o) >= 3:
            n = min(int(o[2]), max(0, _CAP - sum(shed.values())))
            if n > 0:
                shed[o[1]] = shed.get(o[1], 0) + n
    return shed, invs, farm


def _room_guard(observation, action):
    step = int(_g(observation, "step", 0))
    if step % 24 != 23 or step >= 718 or not isinstance(action, dict):
        return action
    shed, invs, farm = _project(observation, action)
    carried = {}
    for inv in invs:
        for k, v in inv.items():
            if v > 0:
                carried[k] = carried.get(k, 0) + v
    excess = sum(v for v in shed.values() if v > 0) + sum(carried.values()) - _CAP
    if excess <= 0:
        return action
    animals = sum(1 for row in _g(farm, "tiles") for t in row
                  if (isinstance(t, dict) or hasattr(t, "keys")) and _g(t, "animal"))
    wheat_spare = shed.get("WHEAT", 0) + carried.get("WHEAT", 0) - (animals + 2)
    prices = _g(_g(observation, "market"), "prices", {})
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    extra = []
    for item in sorted(_SELLABLE, key=lambda it: -int(_g(prices, it, 0))):
        avail = shed.get(item, 0)
        if item == "WHEAT":
            avail = min(avail, max(0, wheat_spare))
        n = min(excess, avail)
        if n <= 0 or int(_g(prices, item, 0)) <= 1:
            continue
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                o[2] = int(o[2]) + n
                break
        else:
            extra.append(["SELL", item, n])
        excess -= n
        if excess <= 0:
            break
    out = dict(action)
    out["market"] = (extra + market)[:10]
    return out


_RACE_FROM = 720
_RACE_SHARE = 1.0
_RACE_ITEMS = ("MILK", "WOOL", "STRAWBERRY", "EGG", "TOMATO", "CARROT")
_SHOP_GOODS = {"BAKERY": ("EGG", "WHEAT"), "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
               "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"), "YARN_STORE": ("WOOL",),
               "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"), "PET_CAFE": ("CARROT",),
               "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
               "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY")}


def _kind(t):
    if not (isinstance(t, dict) or hasattr(t, "keys")):
        return None
    return _g(t, "animal") or _g(t, "crop") or _g(t, "kind")


def _similar(obs):
    """Share of occupied tiles holding the same thing on both farms (cha22-family rivals score ~1)."""
    me = int(_g(obs, "player", 0))
    farms = _g(obs, "farms")
    a, b = _g(farms[me], "tiles"), _g(farms[1 - me], "tiles")
    same = total = 0
    for y in range(len(a)):
        for x in range(len(a[y])):
            ka, kb = _kind(a[y][x]), _kind(b[y][x])
            if ka is None and kb is None:
                continue
            total += 1
            same += ka == kb
    return same / total if total else 0.0


def _race(observation, action):
    """Late game against a same-route rival: when both farms' stock of a premium good exceeds what the
    town can still eat before the end, prices only fall and the first seller wins, so every step after a
    consumption tick our remaining shed stock of that good is sold at the front of the list."""
    step = int(_g(observation, "step", 0))
    if step < _RACE_FROM or step >= 715 or step % 4 != 1 or not isinstance(action, dict):
        return action
    if _similar(observation) < 0.85:
        return action
    shed, invs, farm = _project(observation, action)
    shops = list(_g(_g(observation, "town", {}), "unlocked_shops", []))
    prices = _g(_g(observation, "market"), "prices", {})
    days_left = (718 - step) / 24.0
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    planned = {}
    for o in market:
        if o[0] == "SELL" and len(o) >= 3:
            planned[o[1]] = planned.get(o[1], 0) + int(o[2])
    extra = []
    for item in _RACE_ITEMS:
        spare = shed.get(item, 0)
        if spare <= 0 or int(_g(prices, item, 0)) <= 2:
            continue
        rate = 1.0 + sum((12.0 if len(_SHOP_GOODS.get(sh, ())) == 1 else 6.0)
                         for sh in shops if item in _SHOP_GOODS.get(sh, ()))
        held = spare + planned.get(item, 0) + sum(i.get(item, 0) for i in invs)
        if 2 * held <= rate * days_left:
            continue
        k = int(math.ceil(spare * _RACE_SHARE))
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                o[2] = int(o[2]) + k
                break
        else:
            extra.append(["SELL", item, k])
    if not extra and all(o == p for o, p in zip(market, action.get("market") or [])):
        return action
    out = dict(action)
    sells = [o for o in extra + market if o[0] == "SELL"]
    rest = [o for o in market if o[0] != "SELL"]
    out["market"] = (sells + rest)[:10]
    return out


_OPEN20 = False


def _open20(observation, action):
    """Step 0: the base's own v9 opening trade (BUY 20 / SELL 15 wheat, net +5) instead of the plain BUY 5
    a later base layer puts there; family rivals that beat us open this way."""
    step = int(_g(observation, "step", 0))
    if step != 0 or not isinstance(action, dict):
        return action
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    wheat = [o for o in market if o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == "WHEAT"]
    if len(wheat) != 1 or int(wheat[0][2]) != 5:
        return action
    rest = [o for o in market if o is not wheat[0]]
    out = dict(action)
    out["market"] = [["BUY_PRODUCT", "WHEAT", 20], ["SELL", "WHEAT", 15]] + rest
    return out


_EAGER_FROM = 288
_EAGER_TO = 700
_EAGER_BANDS = {'MILK': (0.3, 0.9), 'STRAWBERRY': (0.3, 0.9), 'WOOL': (0.3, 0.9)}   # item -> (floor, ceiling) as shares of the base price
_SORT_SELLS = True
_SORT_TOL = 10.0
# engine MARKET_PARAMS: base, T, below_func, below_target, above_func, above_target (I0 = 10000)
_MKT = {"WHEAT": (25, 400, "sqrt", 0.80, "log", 0.20), "CARROT": (35, 450, "hinge", 1.00, "sqrt", 0.70),
        "TOMATO": (60, 200, "hinge", 0.40, "sqrt", 0.60), "STRAWBERRY": (120, 100, "sqrt", 0.70, "linear", 1.60),
        "MELON": (250, 300, "log", 0.20, "sq", 3.60), "EGG": (50, 332, "hinge", 0.40, "log", 0.20),
        "MILK": (160, 122, "sqrt", 0.60, "linear", 1.60), "WOOL": (200, 105, "log", 0.20, "sq", 3.20),
        "FERTILIZER": (100, 200, "linear", 0.40, "linear", 0.40)}


def _shape(f, x, T):
    x = max(0.0, x)
    if f == "linear":
        return x
    if f == "sq":
        return x * x
    if f == "sqrt":
        return math.sqrt(x)
    if f == "log":
        return math.log(1.0 + x)
    if f == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _mprice(item, inv):
    base, T, bf, bt, af, at = _MKT[item]
    if inv < 10000:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, 10000 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - 10000, T)
    return max(1, int(round(p)))


def _stake(item, q, inv):
    """What our q units lose if a rival sells as many units of the same item in an earlier slot."""
    if item not in _MKT or q <= 0:
        return 0.0
    q = min(q, 40)
    return float(sum(_mprice(item, inv + k) - _mprice(item, inv + q + k) for k in range(q)))


def _eager(observation, action):
    """Sell premium goods as soon as they reach the shed instead of holding them for the base's
    scheduled lots: in a glutted market the first seller gets the price, and family rivals that
    sell on arrival beat the base's schedule by hundreds of coins."""
    step = int(_g(observation, "step", 0))
    if step < _EAGER_FROM or step >= _EAGER_TO or not isinstance(action, dict):
        return action
    shed, invs, farm = _project(observation, action)
    prices = _g(_g(observation, "market"), "prices", {})
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    free = 10 - len(market)
    changed = False
    for item, (lo, hi) in _EAGER_BANDS.items():
        spare = shed.get(item, 0)
        quote = int(_g(prices, item, 0))
        if spare <= 0 or quote < max(2.0, lo * _MKT[item][0]) or quote > hi * _MKT[item][0]:
            continue
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                o[2] = int(o[2]) + spare
                changed = True
                break
        else:
            if free > 0:
                market.insert(0, ["SELL", item, spare])
                free -= 1
                changed = True
    if not changed:
        return action
    out = dict(action)
    out["market"] = market[:10]
    return out


def _sort_sells(observation, action):
    """Permute the SELL orders among the slots they already occupy, largest stake first: in a same-step
    race the earlier slot sells every unit before the rival's first. An order only moves ahead of one it
    beats by more than _SORT_TOL coins, so a mirror rival's identical list keeps the base's order. A SELL
    after a BUY_PRODUCT of the same item (a wash) stays put; every other order keeps its slot."""
    step = int(_g(observation, "step", 0))
    if step < _SLOT_START or not isinstance(action, dict):
        return action
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
    inv = _g(_g(observation, "market"), "inventory", {})
    bought = set()
    slots, sells = [], []
    for i, o in enumerate(market):
        if o[0] == "BUY_PRODUCT" and len(o) >= 2:
            bought.add(o[1])
        elif o[0] == "SELL" and len(o) >= 3 and o[1] in _MKT and o[1] not in bought:
            slots.append(i)
            sells.append((-_stake(o[1], int(o[2]), int(_g(inv, o[1], 10000))), o))
    if len(sells) < 2:
        return action
    ranked = []
    for s, o in sells:
        pos = len(ranked)
        while pos > 0 and ranked[pos - 1][0] - s > _SORT_TOL:
            pos -= 1
        ranked.insert(pos, (s, o))
    if [o for s, o in ranked] == [o for s, o in sells]:
        return action
    for i, (s, o) in zip(slots, ranked):
        market[i] = o
    out = dict(action)
    out["market"] = market[:10]
    return out


def _v6_agent(observation, configuration=None):
    action = _BASE_AGENT(observation, configuration)
    if _OPEN20:
        try:
            action = _open20(observation, action)
        except Exception:
            pass
    if _EAGER_FROM < 720:
        try:
            action = _eager(observation, action)
        except Exception:
            pass
    try:
        action = _slot_priority(observation, action)
    except Exception:
        pass
    if _RACE_FROM < 720:
        try:
            action = _race(observation, action)
        except Exception:
            pass
    if _GUARD:
        try:
            action = _room_guard(observation, action)
        except Exception:
            pass
    if _SORT_SELLS:
        try:
            action = _sort_sells(observation, action)
        except Exception:
            pass
    return action


# ---- team 42 arena build: v6 + eager-sale band 0.2-1.4x base (MILK/STRAWBERRY/WOOL) + wheat lead-sell 2 steps keeping the next 4 steps of feed pickups
# Everything above is the live v6 (cha22 base, Apache-2.0, with team 42 layers) verbatim, except that its
# final `agent` is renamed `_v6_agent`. Below, team 42 modifications of 2026-09-25 (v7b, v7 with the eager floor at 0.3):
# 5. the eager sale band above is overridden to 0.3x base with no upper cap (MILK, STRAWBERRY, WOOL);
# 6. wheat lead-sell layer: from step 240 to 700, wheat that the route tape sells in the next 2 steps is
#    sold now (order appended last), keeping back the wheat the tape's units pick up from the shed in the
#    next 4 steps (their feed). Layer code from gold/hybrid/layers.py; other layers there are off.

_CFG = {'top': {'_EAGER_BANDS': {'MILK': (0.3, 99.0), 'STRAWBERRY': (0.3, 99.0), 'WOOL': (0.3, 99.0)}}, 'base': {}, 'layers': {'wheat_lead': {'lead': 2, 'hours': [], 'front': False, 'reserve_h': 4}}}


def _lg(o, k, d=None):
    if isinstance(o, dict):
        return o.get(k, d)
    return getattr(o, k, d)


def wrap(cfg, ns):
    """Apply cfg to a namespace holding v6 (its `agent`, `_project` and `_BASE_NS`) and return the layered agent."""
    for k, v in (cfg.get("top") or {}).items():
        ns[k] = v
    for k, v in (cfg.get("base") or {}).items():
        ns["_BASE_NS"][k] = v
    base_agent = ns["agent"]
    chassis = ns["_BASE_NS"]["_IMPL"].chassis
    force = cfg.get("force_route")
    table = cfg.get("route_table")
    late = cfg.get("late_route")
    force_from = int(cfg.get("force_from", 144))
    rules = cfg.get("route_rules") or []
    if force is not None or table or late is not None or rules:
        orig_router = chassis.router

        def router(observation, step, state, _orig=orig_router):
            r = _orig(observation, step, state)
            if late is not None and step >= 648:
                return state.get("_mid_route", r) if late == "keep" else late
            if 144 <= step < 648:
                if rules and step >= 216:
                    shops = list(_lg(_lg(observation, "town", {}), "unlocked_shops", []) or [])
                    if len(shops) >= 3:
                        for rule in rules:
                            if ("|".join(shops[:2]) == rule["pair"] and shops[2] not in rule.get("third_not", ())
                                    and (not rule.get("third_in") or shops[2] in rule["third_in"])):
                                state["_mid_route"] = rule["route"]
                                return rule["route"]
                if force is not None and step >= force_from:
                    r = force
                elif table:
                    key = state.get("_table_key")
                    if key is None:
                        shops = list(_lg(_lg(observation, "town", {}), "unlocked_shops", []) or [])[:2]
                        key = state["_table_key"] = "|".join(shops)
                    r = table.get(key, r)
                state["_mid_route"] = r
            return r
        chassis.router = router
    project = ns["_project"]
    layers = cfg.get("layers") or {}
    mm_state = {}

    def planned(route, step, item, lead):
        tape = chassis.routes.get(route) or []
        q = 0
        for t in range(step + 1, min(len(tape), step + 1 + lead)):
            a = tape[t]
            if isinstance(a, dict):
                for o in a.get("market") or []:
                    if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                        q += int(o[2])
        return q

    def planned_pickups(route, step, item, horizon):
        """Units of `item` the tape's units pick up from the shed in steps step+1 .. step+horizon."""
        tape = chassis.routes.get(route) or []
        q = 0
        for t in range(step + 1, min(len(tape), step + 1 + horizon)):
            a = tape[t]
            if isinstance(a, dict):
                for u in [a.get("farmer")] + list(a.get("hands") or []):
                    if isinstance(u, list) and len(u) >= 3 and u[0] == "PICKUP" and u[1] == item:
                        q += int(u[2])
        return q

    lead_debt = {}

    def lead_sell(obs, action, item, lead, hours, front, reserve_h=0, book=False):
        """Sell now what the route tape sells of `item` in the next `lead` steps. reserve_h > 0 keeps back what the
        tape's units pick up from the shed in the next reserve_h steps (feed); book=True subtracts the early sale from
        the tape's own later SELL orders, so the total sold stays the same and only the timing moves."""
        step = int(_lg(obs, "step", 0))
        player = int(_lg(obs, "player", 0))
        key = (player, item)
        if step == 0:
            lead_debt.pop(key, None)
        if step < 240 or step > 700:
            return action
        st = chassis.players.get(player)
        if not st or st.get("route") is None:
            return action
        market = None
        if book and lead_debt.get(key):
            due_now = sum(n for due, n in lead_debt[key] if due == step)
            lead_debt[key] = [(due, n) for due, n in lead_debt[key] if due > step]
            if due_now > 0:
                market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple)) and o]
                for o in market:
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == item and due_now > 0:
                        cut = min(int(o[2]), due_now)
                        o[2] = int(o[2]) - cut
                        due_now -= cut
                market = [o for o in market if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
                action = dict(action)
                action["market"] = market
        if hours and step % 24 not in hours:
            return action
        plan = planned(st["route"], step, item, lead) - sum(n for due, n in lead_debt.get(key, []))
        if plan <= 0:
            return action
        shed, invs, farm = project(obs, action)
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        selling = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
        reserve = planned_pickups(st["route"], step, item, reserve_h) if reserve_h else 0
        k = min(plan, int(shed.get(item, 0)) - selling - reserve)
        if k <= 0:
            return action
        if book:
            tape = chassis.routes.get(st["route"]) or []
            left = k
            for t in range(step + 1, min(len(tape), step + 1 + lead)):
                a = tape[t]
                if isinstance(a, dict) and left > 0:
                    q = sum(int(o[2]) for o in (a.get("market") or []) if o and o[0] == "SELL" and len(o) >= 3
                            and o[1] == item)
                    take = min(q, left)
                    if take > 0:
                        lead_debt.setdefault(key, []).append((t, take))
                        left -= take
        for i, o in enumerate(market):
            if o[0] == "SELL" and o[1] == item:
                o[2] = int(o[2]) + k
                if front:
                    market.insert(0, market.pop(i))
                break
        else:
            if len(market) >= 10:
                return action
            if front:
                market.insert(0, ["SELL", item, k])
            else:
                market.append(["SELL", item, k])
        out = dict(action)
        out["market"] = market
        return out

    def wheat_mm(obs, action, q, keep):
        step = int(_lg(obs, "step", 0))
        player = int(_lg(obs, "player", 0))
        st = mm_state.get(player)
        if st is None or step == 0:
            st = mm_state[player] = {"held": 0, "buy_step": -9, "before": 0}
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        shed, invs, farm = project(obs, action)
        if st["held"] and step == st["buy_step"] + 1:
            raw = dict(_lg(_lg(obs, "private", {}) or {}, "shed", {}) or {})
            got = int(raw.get("WHEAT", 0)) - st["before"]
            held = max(0, min(st["held"], got))
            if held > 0:
                market.insert(0, ["SELL", "WHEAT", held])
            st["held"] = 0
        elif 264 <= step <= 688 and step % 4 == 0 and step % 24 < 20 and len(market) < 10:
            room = 100 - sum(shed.values()) - sum(int(o[2]) for o in market if o[0] == "BUY_PRODUCT" and len(o) >= 3)
            money = float(_lg(_lg(obs, "farms")[player], "money", 0))
            if room >= q + keep and money > 4000:
                market.append(["BUY_PRODUCT", "WHEAT", q])
                st.update(held=q, buy_step=step, before=int(shed.get("WHEAT", 0)))
        out = dict(action)
        out["market"] = market[:10]
        return out

    opp_state = {}
    product_of = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}

    def opp_race(obs, action, items, min_units, share):
        """Sell our shed stock of a premium good in slot 0 on the step the rival harvests a lot of it: its units
        carry the lot to its shed and sell it a few steps later, so ours reaches the book first."""
        step = int(_lg(obs, "step", 0))
        player = int(_lg(obs, "player", 0))
        farms = _lg(obs, "farms")
        tiles = _lg(farms[1 - player], "tiles")
        snap = {}
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict):
                    item = t.get("crop") or product_of.get(t.get("animal"))
                    if item in items:
                        snap[(x, y)] = (item, int(t.get("yield_units", 0) or 0))
        st = opp_state.get(player)
        opp_state[player] = {"step": step, "snap": snap}
        if st is None or st["step"] != step - 1 or step < 240 or step > 710:
            return action
        harvested = {}
        for xy, (item, y0) in st["snap"].items():
            now = snap.get(xy)
            y1 = now[1] if now and now[0] == item else 0
            if y1 < y0:
                harvested[item] = harvested.get(item, 0) + (y0 - y1)
        hot = [i for i, n in harvested.items() if n >= min_units]
        if not hot:
            return action
        shed, invs, farm = project(obs, action)
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        for item in hot:
            selling = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
            k = int((int(shed.get(item, 0)) - selling) * share)
            if k <= 0:
                continue
            for i, o in enumerate(market):
                if o[0] == "SELL" and o[1] == item:
                    o[2] = int(o[2]) + k
                    market.insert(0, market.pop(i))
                    break
            else:
                if len(market) >= 10:
                    continue
                market.insert(0, ["SELL", item, k])
        out = dict(action)
        out["market"] = market[:10]
        return out

    base_price = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250, "EGG": 50, "MILK": 160,
                  "WOOL": 200, "FERTILIZER": 100}

    def hold_premium(obs, action, items, floor, dump_from, min_room):
        """Drop SELL orders of `items` quoted below floor x base while the shed keeps `min_room` free slots."""
        step = int(_lg(obs, "step", 0))
        if step < 240 or step >= dump_from:
            return action
        shed, invs, farm = project(obs, action)
        prices = _lg(_lg(obs, "market"), "prices")
        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
        room = 100 - sum(shed.values())
        keep = []
        for o in market:
            if o[0] == "SELL" and len(o) >= 3 and o[1] in items:
                px = float(prices.get(o[1], 0) if isinstance(prices, dict) else _lg(prices, o[1], 0))
                n = int(o[2])
                if px < floor * base_price[o[1]] and room - n >= min_room:
                    room -= n
                    continue
            keep.append(o)
        out = dict(action)
        out["market"] = keep
        return out

    mirror_knobs = cfg.get("mirror_knobs") or {}
    mirror_sim = float(cfg.get("mirror_sim", 0.9))
    mirror_from = int(cfg.get("mirror_from", 144))
    base_ns = ns["_BASE_NS"]
    knob_default = {k: base_ns.get(k) for k in mirror_knobs}
    mirror_state = {}

    def tile_key(t):
        if not isinstance(t, dict):
            return t
        return (t.get("kind"), t.get("crop"), t.get("animal"))

    def set_mirror_knobs(obs):
        """Aggressive knobs only while the rival's farm looks like ours (a cha22-family mirror)."""
        step = int(_lg(obs, "step", 0))
        player = int(_lg(obs, "player", 0))
        st = mirror_state.setdefault(player, {"on": False, "last": -99})
        if step == 0:
            st.update(on=False, last=-99)
        if step >= mirror_from and step - st["last"] >= 24:
            st["last"] = step
            farms = _lg(obs, "farms")
            mine, theirs = _lg(farms[player], "tiles"), _lg(farms[1 - player], "tiles")
            same = total = 0
            for y in range(len(mine)):
                for x in range(len(mine[y])):
                    a, b = tile_key(mine[y][x]), tile_key(theirs[y][x])
                    if a in (None, "LOCKED") and b in (None, "LOCKED"):
                        continue
                    total += 1
                    same += a == b
            st["on"] = total > 0 and same / total >= mirror_sim
        for k, v in mirror_knobs.items():
            base_ns[k] = v if st["on"] else knob_default[k]

    def agent(observation, configuration=None):
        if mirror_knobs:
            try:
                set_mirror_knobs(observation)
            except Exception:
                pass
        action = base_agent(observation, configuration)
        for name, p in layers.items():
            if not p:
                continue
            try:
                if name == "fert_lead":
                    action = lead_sell(observation, action, "FERTILIZER", p.get("lead", 3), p.get("hours", [19, 20, 21]),
                                       p.get("front", False))
                elif name == "wheat_lead":
                    action = lead_sell(observation, action, "WHEAT", p.get("lead", 2), p.get("hours", []),
                                       p.get("front", False), p.get("reserve_h", 0), p.get("book", False))
                elif name == "bulk_lead":
                    for item in p.get("items", ["EGG", "TOMATO", "CARROT"]):
                        action = lead_sell(observation, action, item, p.get("lead", 2), p.get("hours", []),
                                           p.get("front", False))
                elif name == "premium_lead":
                    for item in p.get("items", ["MILK", "WOOL", "STRAWBERRY"]):
                        action = lead_sell(observation, action, item, p.get("lead", 2), p.get("hours", []), True)
                elif name == "wheat_mm":
                    action = wheat_mm(observation, action, p.get("q", 30), p.get("keep", 25))
                elif name == "final_dump":
                    step = int(_lg(observation, "step", 0))
                    if p.get("from_step", 696) <= step <= 711:
                        shed, invs, farm = project(observation, action)
                        market = [list(o) for o in (action.get("market") or []) if isinstance(o, list) and o]
                        for item in p.get("items", ["MILK", "WOOL", "STRAWBERRY", "EGG", "TOMATO"]):
                            selling = sum(int(o[2]) for o in market if o[0] == "SELL" and len(o) >= 3 and o[1] == item)
                            k = int(shed.get(item, 0)) - selling
                            if k <= 0:
                                continue
                            for i, o in enumerate(market):
                                if o[0] == "SELL" and o[1] == item:
                                    o[2] = int(o[2]) + k
                                    market.insert(0, market.pop(i))
                                    break
                            else:
                                if len(market) < 10:
                                    market.insert(0, ["SELL", item, k])
                        action = dict(action)
                        action["market"] = market[:10]
                elif name == "hold_premium":
                    action = hold_premium(observation, action, tuple(p.get("items", ["MILK", "WOOL", "STRAWBERRY"])),
                                          p.get("floor", 0.8), p.get("dump_from", 696), p.get("min_room", 20))
                elif name == "opp_race":
                    action = opp_race(observation, action, tuple(p.get("items", ["MILK", "WOOL", "STRAWBERRY"])),
                                      p.get("min_units", 2), p.get("share", 1.0))
            except Exception:
                pass
        return action

    return agent


agent = _v6_agent
_LAYERED = wrap(_CFG, globals())


def agent(observation, configuration=None):
    return _LAYERED(observation, configuration)


# ---------------------------------------------------------------------------
# Team 42 SHEEPFEED fix (outermost layer): see tools/add_sheepfeed.py.
_SF_MOVES = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}


def _sf_ns():
    return globals().get("_BASE_NS") or globals()


def _sf_walk(pos, target):
    x, y = pos
    tx, ty = target
    if x != tx:
        return ["EAST" if x < tx else "WEST"]
    if y != ty:
        return ["SOUTH" if y < ty else "NORTH"]
    return None


_SF_STUCK = {}


def _sheepfeed(obs, action):
    step = int(obs["step"])
    day, hour = divmod(step, 24)
    seat0 = int(obs["player"])
    rec = _SF_STUCK.get(seat0)
    if rec is None or step <= rec["step"]:
        rec = _SF_STUCK[seat0] = {"step": -1, "run": {}, "stall_day": {}}
    rec["step"] = step
    if day < 11 or step >= 717 or not isinstance(action, dict):
        return action
    seat = int(obs["player"])
    st = (_sf_ns().get("_V233_STATES") or {}).get(seat)
    if not st or not st.get("committed") or not st.get("workers"):
        return action
    farm = obs["farms"][seat]
    priv = obs["private"]
    tiles = farm["tiles"]
    hands = farm["hands"]
    units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in hands]
    access = {(4, 4), (5, 4), (4, 5), (5, 5)}
    invs = priv.get("inventories") or []
    shed_wheat = int((priv.get("shed") or {}).get("WHEAT", 0))
    sheep = {}
    for targets in st["workers"].values():
        for x, y in targets:
            t = tiles[y][x]
            if isinstance(t, dict) and t.get("animal") == "SHEEP":
                sheep[(x, y)] = t
    hungry = [xy for xy, t in sheep.items() if not t.get("fed_today")]
    changed = False
    stalled = False
    # wheat the earlier units pick up this turn, in engine order (farmer, then hands by index)
    left = shed_wheat
    for i, cmd in enumerate(units[:len(positions)]):
        pickup = bool(cmd) and cmd[0] == "PICKUP" and len(cmd) >= 2 and cmd[1] == "WHEAT" and positions[i] in access
        want = (int(cmd[2]) if len(cmd) >= 3 else 1) if pickup else 0
        if i in st["workers"]:
            if pickup:
                stuck_now = want <= 0 or left <= 0
                run = rec["run"].get(i, 0) + 1 if stuck_now else 0
                rec["run"][i] = run
                if stuck_now and run >= 2:   # a real deadlock: nothing to pick up on two turns in a row
                    rec["stall_day"][i] = day
            if rec["stall_day"].get(i) == day:
                # take the worker over for the day while it cannot get wheat from the shed
                stalled = True
                inv = invs[i] if i < len(invs) else {}
                pos = positions[i]
                new = None
                if int(inv.get("WHEAT", 0)) > 0 and hungry:
                    here = sheep.get(pos)
                    if not (cmd == ["FEED"] and here is not None and not here.get("fed_today")):
                        target = min(hungry, key=lambda xy: (abs(pos[0] - xy[0]) + abs(pos[1] - xy[1]), xy))
                        new = _sf_walk(pos, target) or ["FEED"]
                elif left <= 0 or not hungry:
                    todo = [xy for xy, t in sheep.items() if t.get("fed_today") and not t.get("cared_today")]
                    todo = todo or [xy for xy, t in sheep.items() if int(t.get("yield_units", 0)) > 0]
                    if todo:
                        target = min(todo, key=lambda xy: (abs(pos[0] - xy[0]) + abs(pos[1] - xy[1]), xy))
                        t = sheep[target]
                        new = _sf_walk(pos, target) or (["CARE"] if t.get("fed_today") and not t.get("cared_today")
                                                         else ["HARVEST"])
                if new:
                    units[i] = new
                    changed = True
                    continue
        if pickup:
            left -= min(max(0, want), left)
    carried = sum(int((invs[i] if i < len(invs) else {}).get("WHEAT", 0)) for i in st["workers"])
    short = len(hungry) - carried - left
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple)) and o]
    if stalled and short > 0 and hour <= 20:
        for o in market:
            if short > 0 and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT" and int(o[2]) > 0:
                cut = min(int(o[2]), short)
                o[2] = int(o[2]) - cut
                short -= cut
                changed = True
        buying = sum(int(o[2]) for o in market if o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == "WHEAT")
        need = min(6, short - buying)
        quote = int((obs["market"]["prices"] or {}).get("WHEAT", 0))
        if need > 0 and 0 < quote and float(farm.get("money", 0)) > 1000 + need * (quote + 10):
            for o in market:
                if o[0] == "BUY_PRODUCT" and len(o) >= 3 and o[1] == "WHEAT":
                    o[2] = int(o[2]) + need
                    break
            else:
                if len(market) >= 10:
                    market = [o for o in market if not (o[0] == "SELL" and len(o) >= 3 and int(o[2]) <= 0)]
                if len(market) < 10:
                    market.insert(0, ["BUY_PRODUCT", "WHEAT", need])
            changed = True
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"] = units[0], units[1:]
    out["market"] = market[:10]
    return out


_PRE_SF_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_SF_AGENT(observation, configuration)
    try:
        return _sheepfeed(observation, action)
    except Exception:
        return action


# ---------------------------------------------------------------------------
# Team 42 FERTMORE layer (outermost): see tools/add_fertmore.py.
_FM_FROM, _FM_TO = 288, 690
_FM_EXTRA = 0   # extra units taken at the route's own fertilizer pickups
_FM_EXTRA_FROM = 20   # from this day (the fertilizer book is worth $10-20 by then)
# crop: (first_yield_day, max_yield_day, max_yield, ongoing, interval)
_FM_CROPS = {"WHEAT": (2, 4, 6, False, 0), "CARROT": (2, 3, 4, False, 0),
             "TOMATO": (8, 8, 4, True, 1), "STRAWBERRY": (10, 10, 4, True, 2)}
_FM_ACCESS = ((4, 4), (5, 4), (4, 5), (5, 5))
_FM_STEPS = {"NORTH": (0, -1), "SOUTH": (0, 1), "EAST": (1, 0), "WEST": (-1, 0)}
_FM_CACHE = {}


def _fm_ns():
    return globals().get("_BASE_NS") or globals()


def _fm_spawn(positions):
    occ = {a: 0 for a in _FM_ACCESS}
    for p in positions:
        if tuple(p) in occ:
            occ[tuple(p)] += 1
    return min(_FM_ACCESS, key=lambda a: (occ[a], _FM_ACCESS.index(a)))


def _fm_tape_waters(seat, day):
    """Tiles the route's own units water on `day` (farmer from (4, 4), hands spawned by the tape's hires)."""
    key = (seat, day)
    if key in _FM_CACHE:
        return _FM_CACHE[key]
    chassis = _fm_ns()["_IMPL"].chassis
    native = chassis.players.get(seat)
    out = set()
    if native and native.get("route") is not None and day <= 29:
        pos = [(4, 4)]
        for t in range(day * 24, min(719, day * 24 + 24)):
            tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
            a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
            cmds = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for i in range(len(pos)):
                c = cmds[i] if i < len(cmds) and cmds[i] else ["PASS"]
                if c[0] in _FM_STEPS:
                    dx, dy = _FM_STEPS[c[0]]
                    nx, ny = pos[i][0] + dx, pos[i][1] + dy
                    if 0 <= nx < 10 and 0 <= ny < 10:
                        pos[i] = (nx, ny)
                elif c[0] == "WATER":
                    out.add(pos[i])
            for o in a.get("market") or []:
                if o and o[0] == "HIRE":
                    pos.append(_fm_spawn(pos))
    if len(_FM_CACHE) > 16:
        _FM_CACHE.clear()
    _FM_CACHE[key] = out
    return out


def _fm_gain_units(t, day, replacing_water, tomorrow_watered):
    spec = _FM_CROPS.get(t.get("crop"))
    if not spec:
        return 0.0
    first, maxday, maxy, ongoing, interval = spec
    planted = int(t["planted_day"])
    fu = int(t.get("fertilized_until_day", -1))
    watered = bool(t.get("watered_today"))
    if not ongoing:
        ws = (maxday + 1) // 2
        covered = 0
        for d in (day, day + 1, day + 2):
            a = d - planted
            if a < ws or a > maxday or d <= fu:
                continue
            if d == day and (replacing_water or watered):
                continue
            covered += 1
        remaining = sum(1 for d in range(day, planted + maxday + 1)
                        if d - planted >= ws and not (d == day and watered))
        room = max(0, maxy - int(t.get("yield_units", 0)) - remaining)
        return 0.75 * min(covered, room)
    units = 0
    for e in (day, day + 1, day + 2):
        if e > 28 or e <= fu:
            continue
        dsf = e + 1 - planted - first
        if dsf < 0 or dsf % interval or dsf // interval + 1 > maxy:
            continue
        if e == day and not watered:
            continue
        if e == day + 1 and not tomorrow_watered:
            continue
        units += 1
    return 0.9 * units


def _fertmore(obs, action):
    step = int(obs["step"])
    day = step // 24
    if step < _FM_FROM or step > _FM_TO or not isinstance(action, dict):
        return action
    seat = int(obs["player"])
    chassis = _fm_ns()["_IMPL"].chassis
    native = chassis.players.get(seat)
    if not native or native.get("route") is None:
        return action
    farm = obs["farms"][seat]
    priv = obs["private"]
    tiles = farm["tiles"]
    positions = [tuple(farm["farmer"])] + [tuple(h) for h in farm["hands"]]
    invs = priv.get("inventories") or []
    units = [list(action.get("farmer") or ["PASS"])] + [list(c) for c in (action.get("hands") or [])]
    prices = obs["market"]["prices"]
    fquote = float(prices.get("FERTILIZER", 0))
    tape = chassis.routes.get(2 if step >= 648 else native["route"]) or []
    planned = {}
    for tt in range(step + 1, min(len(tape), day * 24 + 24)):
        a = tape[tt] if isinstance(tape[tt], dict) else {}
        for u, c in enumerate([a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])):
            if c and c[0] == "FERTILIZE":
                planned[u] = planned.get(u, 0) + 1
    tomorrow = None
    targeted = set()
    changed = False
    if _FM_EXTRA > 0 and day >= _FM_EXTRA_FROM:
        # the route's own fertilizer pickups take a few more units to spend along the way, but only out of
        # stock that no later pickup of the route needs today
        later = 0
        for tt in range(step + 1, min(len(tape), day * 24 + 24)):
            a = tape[tt] if isinstance(tape[tt], dict) else {}
            for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
                if c and c[0] == "PICKUP" and len(c) >= 3 and c[1] == "FERTILIZER":
                    later += max(0, int(c[2]))
        shed_f = int((priv.get("shed") or {}).get("FERTILIZER", 0)) - later
        for u, cmd in enumerate(units[:len(positions)]):
            if cmd and cmd[0] == "PICKUP" and len(cmd) >= 2 and positions[u] in _FM_ACCESS:
                want = max(0, int(cmd[2]) if len(cmd) >= 3 else 1)
                if cmd[1] == "FERTILIZER":
                    extra = min(_FM_EXTRA, max(0, shed_f - want))
                    if extra > 0:
                        units[u] = ["PICKUP", "FERTILIZER", want + extra]
                        changed = True
                    shed_f -= min(shed_f, want + max(0, extra))
    for u, cmd in enumerate(units[:len(positions)]):
        inv = invs[u] if u < len(invs) else {}
        spare = int(inv.get("FERTILIZER", 0)) - planned.get(u, 0)
        if spare <= 0:
            continue
        pos = positions[u]
        t = tiles[pos[1]][pos[0]]
        if not (isinstance(t, dict) and t.get("kind") == "PLANT") or pos in targeted:
            continue
        crop = t.get("crop")
        if crop not in _FM_CROPS:
            continue
        op = cmd[0] if cmd else "PASS"
        replacing = False
        if op == "PASS" or (op == "WATER" and t.get("watered_today")):
            pass
        elif op == "WATER" and int(t.get("consecutive_unwatered", 1)) == 0:
            age = day - int(t["planted_day"])
            if crop in ("WHEAT", "CARROT") and age == 1:
                replacing = True
            elif crop == "STRAWBERRY":
                first, maxday, maxy, ongoing, interval = _FM_CROPS[crop]
                dsf = day + 1 - int(t["planted_day"]) - first
                if dsf >= 0 and dsf % interval == 0:
                    continue          # production tonight: keep today's water
                if tomorrow is None:
                    tomorrow = _fm_tape_waters(seat, day + 1)
                if pos not in tomorrow:
                    continue
                replacing = True
            else:
                continue
        else:
            continue
        tw = True
        if t.get("crop") in ("STRAWBERRY", "TOMATO"):
            if tomorrow is None:
                tomorrow = _fm_tape_waters(seat, day + 1)
            tw = pos in tomorrow
        value = _fm_gain_units(t, day, replacing, tw) * float(prices.get(crop, 0))
        if value <= fquote + 5:
            continue
        units[u] = ["FERTILIZE"]
        targeted.add(pos)
        changed = True
    if not changed:
        return action
    out = dict(action)
    out["farmer"], out["hands"] = units[0], units[1:]
    return out


_PRE_FM_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_FM_AGENT(observation, configuration)
    try:
        return _fertmore(observation, action)
    except Exception:
        return action

# ---------------------------------------------------------------------------
# Team 42 TICK layer (outermost), 2026-09-25: wheat tick arbitrage. The town eats wheat right after
# the market of every step s with s % 4 == 0. At such steps (day 10 on) buy up to N wheat in the last
# order slot, N capped by shed room that stays safe if every unit ending the step on a shed tile drops
# its bag at s + 1, and by spare cash; sell the same wheat at s + 1 (joined to the base wheat sell or
# right after the leading sells). The base policy sees the shed without that wheat. Stops for the rest
# of the game once the rival is seen doing the same (its wheat flow is inferred from the market).
_TICK_SRC = r'''import copy as _copy
import math as _math
CFG = {'FROM_DAY': 13, 'NMAX': 95, 'RESERVE': 1500.0, 'MIN_GAIN': 3.0, 'MARGIN': 3, 'NEAR': 1, 'BUYSLOT': 'pad', 'SELLSLOT': 'after', 'GUARD': 1, 'TH': 10, 'WIN': 8, 'HITS': 2, 'RESUME': 6, 'FADEGUARD': 1}
TEL = {"buys": 0, "units": 0, "sold": 0, "skips_full": 0, "carry": 0}
_WSHOPS = {"BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "ICE_CREAM_SHOP", "FARMERS_MARKET"}
_FIB = [1, 1]
while len(_FIB) < 40:
    _FIB.append(_FIB[-1] + _FIB[-2])
_PRICE = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
_SEED = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_AMP_B = 0.8 * 25 / _math.sqrt(400)
_AMP_A = 0.2 * 25 / _math.log(401)
_MEM = {}
_SHED = frozenset(((4, 4), (5, 4), (4, 5), (5, 5)))
_MOVES = {"MOVE_UP": (0, -1), "MOVE_DOWN": (0, 1), "MOVE_LEFT": (-1, 0), "MOVE_RIGHT": (1, 0),
          "UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0),
          "NORTH": (0, -1), "SOUTH": (0, 1), "WEST": (-1, 0), "EAST": (1, 0)}


def _wp(inv):
    if inv < 10000:
        p = 25 + _AMP_B * _math.sqrt(10000 - inv)
    else:
        p = 25 - _AMP_A * _math.log(1 + inv - 10000)
    return max(1, int(round(p)))


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _spend(prices, market, hires_today):
    s = 0.0
    h = hires_today
    for o in market:
        if not o:
            continue
        if o[0] == "HIRE":
            s += _FIB[min(39, h)]
            h += 1
        elif o[0] == "BUY_LAND":
            s += 4000
        elif o[0] == "BUY_ANIMAL" and len(o) >= 3:
            s += _PRICE.get(o[1], 500) * int(o[2])
        elif o[0] == "BUY_SEED" and len(o) >= 3:
            s += _SEED.get(o[1], 100) * int(o[2])
        elif o[0] == "BUY_PRODUCT" and len(o) >= 3:
            s += (int(_get(prices, o[1], 50)) + 6) * int(o[2])
    return s


def _net_wheat(market):
    n = 0
    for o in market:
        if o and len(o) >= 3 and o[1] == "WHEAT":
            if o[0] == "SELL":
                n += int(o[2])
            elif o[0] == "BUY_PRODUCT":
                n -= int(o[2])
    return n


def _doctor(observation, hide):
    obs = _copy.deepcopy(observation)
    priv = _get(obs, "private")
    shed = dict(_get(priv, "shed", {}) or {})
    shed["WHEAT"] = max(0, int(shed.get("WHEAT", 0)) - hide)
    try:
        priv["shed"] = shed
    except Exception:
        setattr(priv, "shed", shed)
    return obs


def _cons(observation, step):
    if step % 4 != 0:
        return 0
    town = _get(observation, "town", {}) or {}
    shops = list(_get(town, "unlocked_shops", []) or [])
    return sum(1 for s in shops if s in _WSHOPS) + (1 if step % 24 == 0 else 0)


def _track(mem, observation, step, a):
    """Infer the rival's net wheat flow of the previous step from the market identity
    dI = our net sold + rival net sold - town use; flag a rival that buys at s % 4 == 0 and sells at s + 1."""
    mk = _get(observation, "market", {}) or {}
    inv_w = int((_get(mk, "inventory", {}) or {}).get("WHEAT", 10000))
    w_now = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
    prev = mem.get("prev")
    if prev is not None and prev["step"] == step - 1 and prev["step"] % 24 != 23:
        our_net = prev["w_units"] - w_now
        mem["flow"][prev["step"]] = (inv_w - prev["inv"]) - our_net + prev["cons"]
    try:
        w_units = int(_PROJECT(observation, dict(a, market=[]))[0].get("WHEAT", 0))
    except Exception:
        w_units = w_now
    mem["prev"] = {"step": step, "inv": inv_w, "w_units": w_units, "cons": _cons(observation, step)}
    if step % 4 == 2:
        fl = mem["flow"]
        hits = 0
        last = None
        for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
            churn = fl.get(s0, 0) <= -CFG["TH"] and fl.get(s0 + 1, 0) >= CFG["TH"]
            fade = CFG.get("FADEGUARD") and fl.get(s0, 0) >= CFG["TH"] and fl.get(s0 + 1, 0) <= -CFG["TH"]
            if churn or fade:
                hits += 1
                if last is None:
                    last = s0
        if not mem["rival"]:
            if hits >= CFG["HITS"]:
                mem["rival"] = True
                TEL["rival_step"] = step
        elif CFG.get("RESUME") and (last is None or step - 2 - last >= 4 * CFG["RESUME"]):
            mem["rival"] = False
            TEL["resumes"] = TEL.get("resumes", 0) + 1


def _decide(observation, configuration=None):
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return _BASE(observation, configuration)
    mem = _MEM.setdefault(me, {"pend": None, "last": -1})
    if step <= mem["last"]:
        mem.clear()
        mem.update({"pend": None, "last": -1})
    mem.setdefault("flow", {})
    mem.setdefault("rival", False)
    mem["last"] = step
    pend = mem["pend"]
    hide = 0
    if pend is not None:
        try:
            shed_w = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
            hide = max(0, min(pend["n"], shed_w - pend["without"]))
        except Exception:
            hide = 0
    obs_in = observation
    if hide > 0:
        try:
            obs_in = _doctor(observation, hide)
        except Exception:
            obs_in = observation
    a = _BASE(obs_in, configuration)
    try:
        if not isinstance(a, dict):
            return a
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple)) and o]
        if pend is not None:
            mem["pend"] = None
            if hide > 0:
                placed = False
                if CFG["SELLSLOT"] == "first" and len(market) < 10:
                    market.insert(0, ["SELL", "WHEAT", hide])
                    placed = True
                for o in ([] if placed else market):
                    if o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT":
                        o[2] = int(o[2]) + hide
                        placed = True
                        break
                if not placed and len(market) < 10:
                    i = 0
                    while i < len(market) and market[i][0] == "SELL":
                        i += 1
                    market.insert(i, ["SELL", "WHEAT", hide])
                    placed = True
                if placed:
                    TEL["sold"] += hide
                else:
                    TEL["carry"] += 1
                    mem["pend"] = {"n": hide, "without": pend["without"], "step": step}
            a = dict(a)
            a["market"] = market
            if mem["pend"] is not None:
                return a
        if step % 4 != 0 or step // 24 < CFG["FROM_DAY"] or step > 716:
            return a
        if mem.get("rival"):
            TEL["rival_skips"] = TEL.get("rival_skips", 0) + 1
            return a
        if len(market) >= 10:
            TEL["skips_full"] += 1
            return a
        town = _get(observation, "town", {}) or {}
        shops = list(_get(town, "unlocked_shops", []) or [])
        c = sum(1 for s in shops if s in _WSHOPS) + (1 if step % 24 == 0 else 0)
        if c <= 0:
            return a
        mk = _get(observation, "market", {}) or {}
        inv_w = int((_get(mk, "inventory", {}) or {}).get("WHEAT", 10000))
        prices = _get(mk, "prices", {}) or {}
        proj = _PROJECT(observation, dict(a, market=market))
        pshed, pinvs = proj[0], proj[1]
        carried = 0
        if CFG["NEAR"]:
            me_f = _get(observation, "farms")[me]
            pos = [tuple(_get(me_f, "farmer"))] + [tuple(h) for h in (_get(me_f, "hands", []) or [])]
            units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for idx, inv in enumerate(pinvs):
                if idx >= len(pos):
                    break
                x, y = pos[idx]
                act = units[idx] if idx < len(units) else ["PASS"]
                if isinstance(act, list) and act and act[0] in _MOVES:
                    dx, dy = _MOVES[act[0]]
                    x, y = x + dx, y + dy
                if (x, y) in _SHED:
                    carried += sum(int(v) for v in inv.values() if int(v) > 0)
        else:
            carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - CFG["MARGIN"]
        me_farm = _get(observation, "farms")[me]
        money = float(_get(me_farm, "money", 0))
        spend = _spend(prices, market, int(_get(me_farm, "hires_today", 0) or 0))
        cash = money - spend - CFG["RESERVE"]
        I = inv_w + _net_wheat(market)
        n = min(int(CFG["NMAX"]), room)
        TEL["lim_room"] = TEL.get("lim_room", 0) + (room < int(CFG["NMAX"]))
        cost = 0
        k = 0
        while k < n:
            p = _wp(I - k - 1)
            if cost + p > cash:
                break
            cost += p
            k += 1
        TEL["lim_cash"] = TEL.get("lim_cash", 0) + (k < n)
        n = k
        if n < 10:
            return a
        gain = sum(_wp(I - j) for j in range(n + 1, n + c + 1)) - sum(_wp(I - j) for j in range(1, c + 1))
        if gain < CFG["MIN_GAIN"]:
            return a
        if CFG["BUYSLOT"] == "pad":
            while len(market) < 9:
                market.append([])
        market.append(["BUY_PRODUCT", "WHEAT", n])
        mem["pend"] = {"n": n, "without": int(pshed.get("WHEAT", 0)), "step": step}
        TEL["buys"] += 1
        TEL["units"] += n
        a = dict(a)
        a["market"] = market
    except Exception:
        pass
    return a


def agent(observation, configuration=None):
    a = _decide(observation, configuration)
    try:
        if CFG["GUARD"] and isinstance(a, dict):
            step = int(_get(observation, "step", 0))
            me = int(_get(observation, "player", 0))
            _track(_MEM[me], observation, step, a)
    except Exception:
        pass
    return a
'''
_PRE_TICK_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order
_TICK_NS = {"__name__": "tick_layer", "_BASE": _PRE_TICK_AGENT, "_PROJECT": _project}
exec(compile(_TICK_SRC, "tick_layer", "exec"), _TICK_NS)
_TICK = _TICK_NS["agent"]


def agent(observation, configuration=None):
    return _TICK(observation, configuration)


# ---------------------------------------------------------------------------
# Team 42 FADE layer (outermost): see tools/add_fade.py.
_FD_XMAX = 90
_FD_MIN_N = 15
_FD_RESERVE = 1500.0
_FD_STATE = {}
_FD_REPORT = {"sells": 0, "sold": 0, "buys": 0, "bought": 0, "active_steps": 0}


def _fd_pickups(seat, step, horizon):
    ns = globals().get("_BASE_NS") or globals()
    chassis = ns["_IMPL"].chassis
    native = chassis.players.get(seat)
    if not native or native.get("route") is None:
        return 0
    total = 0
    for t in range(step + 1, min(719, step + 1 + horizon)):
        tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
        a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
        for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
            if c and c[0] == "PICKUP" and len(c) >= 2 and c[1] == "WHEAT":
                total += max(0, int(c[2]) if len(c) >= 3 else 1)
    return total


def _fd_rival_n(mem, step):
    """Mean size of the rival's recent churn buys (0 when it has not churned in the last 4 ticks)."""
    fl = mem.get("flow") or {}
    sizes = []
    for s0 in range(step - 4, step - 4 - 16, -4):
        b, s1 = fl.get(s0, 0), fl.get(s0 + 1, 0)
        if b <= -_FD_MIN_N and s1 >= _FD_MIN_N:
            sizes.append(min(-b, s1))
    return sum(sizes) / len(sizes) if len(sizes) >= 2 else 0


def _fd_place(market, order):
    """Put the order in the last slot (index 9), padding with empty orders, so it fills after every rival order
    placed earlier in the list; an empty pad of an earlier layer is reused when the list is full."""
    if len(market) >= 10:
        slot = next((i for i, o in enumerate(market) if not o), None)
        if slot is None:
            return False
        market.pop(slot)
    while len(market) < 9:
        market.append([])
    market.append(order)
    return True


def _fade(obs, action):
    step = int(obs["step"])
    seat = int(obs["player"])
    st = _FD_STATE.get(seat)
    if st is None or step <= st["step"]:
        st = _FD_STATE[seat] = {"step": -1, "sold": {}}
    st["step"] = step
    if not isinstance(action, dict) or step < 240 or step > 717:
        return action
    if st.get("off"):   # v12_5: switched off by the outer guard once the fade rounds stop paying; sell the lot once
        if not st.get("liq") and step <= 716:
            st["liq"] = True
            try:
                market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
                shed_w = int(_project(obs, dict(action, market=[o for o in market if o]))[0].get("WHEAT", 0))
                y = int(min(_FD_XMAX, shed_w - _fd_pickups(seat, step, 6)))
                if y >= 5 and _fd_place(market, ["SELL", "WHEAT", y]):
                    _FD_REPORT["liquidated"] = _FD_REPORT.get("liquidated", 0) + y
                    out = dict(action)
                    out["market"] = market[:10]
                    return out
            except Exception:
                pass
        return action
    mem = (_TICK_NS.get("_MEM") or {}).get(seat) or {}
    if not mem.get("rival"):
        return action
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    farm = obs["farms"][seat]
    money = float(farm.get("money", 0))
    prices = obs["market"]["prices"]
    quote = int(prices.get("WHEAT", 40))
    changed = False
    try:
        shed_w = int(_project(obs, dict(action, market=[o for o in market if o]))[0].get("WHEAT", 0))
    except Exception:
        return action
    if step % 4 == 0 and step <= 716:
        n = _fd_rival_n(mem, step)
        if n > 0:
            _FD_REPORT["active_steps"] += 1
            reserve = _fd_pickups(seat, step, 3)
            x = int(min(_FD_XMAX, n, shed_w - reserve))
            if x > 0:
                x = x if _fd_place(market, ["SELL", "WHEAT", x]) else 0
                if x > 0:
                    st["sold"][step] = (x, shed_w)
                    _FD_REPORT["sells"] += 1
                    _FD_REPORT["sold"] += x
                    changed = True
    elif step % 4 == 1 and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"]):
        st["sold"].pop(step - 1, None)
        # after the rival's unwind the book is at its low: restock the fading lot (XMAX above the route's
        # pickups of the next steps), within shed room and cash
        want = max(0, _FD_XMAX + _fd_pickups(seat, step, 4) - shed_w)
        # the lot stays in the shed for several steps: keep room for everything the units carry (a DROP into a
        # full shed deletes goods)
        pshed, pinvs = _project(obs, dict(action, market=[o for o in market if o]))[:2]
        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        cash = money - _FD_RESERVE
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want > 0:
            want = want if _fd_place(market, ["BUY_PRODUCT", "WHEAT", want]) else 0
            if want > 0:
                _FD_REPORT["buys"] += 1
                _FD_REPORT["bought"] += want
                changed = True
    if not changed:
        return action
    out = dict(action)
    out["market"] = market[:10]
    return out


_PRE_FD_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    action = _PRE_FD_AGENT(observation, configuration)
    try:
        return _fade(observation, action)
    except Exception:
        return action
# Team 42 change (v12_1, 2026-09-26): the TICK layer starts on day 13 instead of day 10, so rival churners
# that back off when they see our churn (most start on days 10-12) churn first and are faded.

# ---------------------------------------------------------------------------
# Team 42 SCHEDULED FADE layer (outermost, v12_2): about 50 teams run a public layer that buys 63-89 wheat at the
# fixed steps 327, 375, 419, 435, 487 (s % 4 == 3) and sells it the next step. One step earlier we buy up to 80
# wheat in the last slot and sell it in the last slot of the scheduled step, after the rival's buy lifted the
# price. The first scheduled step is played blind; later ones only after the rival was seen doing it.
_SCH_SRC = r'''import copy as _copy
CFG = {'XMAX': 80, 'SCHED': [327, 375, 419, 435, 487], 'LEAD': 1, 'RESERVE': 1500.0, 'GATE': 1}
TEL = {"prebuys": 0, "prebought": 0, "sells": 0, "sold": 0}
_MEM = {}


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _pad_last(market, order):
    if len(market) >= 10:
        slot = next((i for i, o in enumerate(market) if not o), None)
        if slot is None:
            return False
        market.pop(slot)
    while len(market) < 9:
        market.append([])
    market.append(order)
    return True


def _armed(me, target):
    """GATE 0: always. GATE 1: the first scheduled step blind, later ones only after the rival was seen buying 20+
    at a scheduled step and selling 20+ the step after (inferred from the TICK layer's rival wheat flow)."""
    if not CFG["GATE"]:
        return True
    first = CFG["SCHED"][0]
    if target == first:
        return CFG["GATE"] == 1
    try:
        fl = (_NS["_TICK_NS"]["_MEM"].get(me) or {}).get("flow") or {}
    except Exception:
        return False
    for s0 in CFG["SCHED"]:
        if s0 >= target:
            break
        if fl.get(s0, 0) <= -20 and fl.get(s0 + 1, 0) >= 20:
            return True
    return False


def agent(observation, configuration=None):
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return _BASE(observation, configuration)
    mem = _MEM.setdefault(me, {"last": -1, "lot": 0, "base_w": 0})
    if step <= mem["last"]:
        mem.update({"lot": 0, "base_w": 0})
    mem["last"] = step
    sched = CFG["SCHED"]
    obs_in = observation
    hide = 0
    if step in sched and mem["lot"] > 0:
        shed_w = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
        hide = max(0, min(mem["lot"], shed_w - mem["base_w"]))
        if hide > 0:
            try:
                obs_in = _copy.deepcopy(observation)
                pv = _get(obs_in, "private")
                sh = dict(_get(pv, "shed", {}) or {})
                sh["WHEAT"] = max(0, int(sh.get("WHEAT", 0)) - hide)
                pv["shed"] = sh
            except Exception:
                obs_in = observation
    a = _BASE(obs_in, configuration)
    try:
        if not isinstance(a, dict):
            return a
        market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple))]
        changed = False
        if step in sched:
            if hide > 0 and _pad_last(market, ["SELL", "WHEAT", hide]):
                TEL["sells"] += 1
                TEL["sold"] += hide
                changed = True
            mem["lot"] = 0
        elif (step + CFG["LEAD"]) in sched and _armed(me, step + CFG["LEAD"]):
            live = [o for o in market if o]
            pshed, pinvs = _PROJECT(observation, dict(a, market=live))[:2]
            carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
            room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
            farm = _get(observation, "farms")[me]
            money = float(_get(farm, "money", 0))
            quote = int(_get(_get(_get(observation, "market", {}) or {}, "prices", {}) or {}, "WHEAT", 40))
            x = int(max(0, min(CFG["XMAX"], room, (money - CFG["RESERVE"]) // max(1, quote + 8))))
            if x >= 10 and _pad_last(market, ["BUY_PRODUCT", "WHEAT", x]):
                mem["lot"] = x
                mem["base_w"] = int(pshed.get("WHEAT", 0))
                TEL["prebuys"] += 1
                TEL["prebought"] += x
                changed = True
        if changed:
            a = dict(a)
            a["market"] = market[:10]
    except Exception:
        pass
    return a
'''
_PRE_SCH_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order
_SCH_NS = {"__name__": "sched_fade_layer", "_BASE": _PRE_SCH_AGENT, "_PROJECT": _project, "_NS": globals()}
exec(compile(_SCH_SRC, "sched_fade_layer", "exec"), _SCH_NS)
_SCH_AGENT = _SCH_NS["agent"]


def agent(observation, configuration=None):
    return _SCH_AGENT(observation, configuration)

# ---------------------------------------------------------------------------
# Team 42 TICK TRAP GUARD layer (outermost, v12_3; v12_5 adds a FADE profit guard). Some rivals trap the TICK
# layer's wheat round trip: at s % 4 == 0 they buy 80-90 wheat in slot 0 and sell as much in slot 9, against our
# last-slot tick buy (net flow zero, so the flow guard cannot see it), or they buy one step before our tick buy
# and sell with our tick sell. Money moves only in the market, so each step the cash of our own final orders is
# simulated alone with the engine's rules and compared with the realized cash one step later. Three of the last
# four tick cycles losing 40+ (or the prebuy flow pattern twice) pause TICK for the game, and a counter sells a
# wheat lot into the rival's lift (middle slot) and buys it back in the last slot after its sell, while that
# keeps paying. v12_5: each FADE round (sell leg at s % 4 == 0, buy leg at s + 1) is priced exactly from the
# next observation's wheat inventory (both legs sit in the last order slot); when the last four rounds average
# no gain per unit, the FADE layer is switched off for the rest of the game and its lot is sold.
_TG_SRC = r'''
import math as _math
CFG = {'ACT': 1, 'K': 4, 'NB': 3, 'BAD': 40.0, 'LOSS': 0.0, 'UNTIL': 700, 'PREBUY': 1, 'TH': 25, 'HITS': 2, 'WIN': 8, 'LOG': 0, 'CF': 1, 'CF_X': 80, 'CF_SLOT': 2, 'CF_MIN_N': 15, 'CF_UNTIL': 688, 'CF_RESERVE': 1500.0, 'CF_K': 8, 'CF_SPIKE': 60.0, 'CF_SPARE0': 1, 'CF_PICK': 2, 'CF_STOCK': 1, 'CF_PREBUY': 1, 'FG': 1, 'FG_K': 4, 'FG_MIN': -1.2}
TEL = {"devs": [], "cycles": [], "trap_step": None, "prebuy_step": None}
_MEM = {}
_MP = {
    "WHEAT": (25, 400, "sqrt", 0.80, "log", 0.20),
    "CARROT": (35, 450, "hinge", 1.00, "sqrt", 0.70),
    "TOMATO": (60, 200, "hinge", 0.40, "sqrt", 0.60),
    "STRAWBERRY": (120, 100, "sqrt", 0.70, "linear", 1.60),
    "MELON": (250, 300, "log", 0.20, "sq", 3.60),
    "EGG": (50, 332, "hinge", 0.40, "log", 0.20),
    "MILK": (160, 122, "sqrt", 0.60, "linear", 1.60),
    "WOOL": (200, 105, "log", 0.20, "sq", 3.20),
    "FERTILIZER": (100, 200, "linear", 0.40, "linear", 0.40),
}
_SHOPS = {
    "BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"], "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE": ["WOOL"], "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"],
    "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
_SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
_LAND = [1000, 2000, 4000]
_FIBS = [1, 1]
while len(_FIBS) < 60:
    _FIBS.append(_FIBS[-1] + _FIBS[-2])


def _shape(f, x, T):
    x = max(0.0, x)
    if f == "linear":
        return x
    if f == "sq":
        return x * x
    if f == "sqrt":
        return _math.sqrt(x)
    if f == "log":
        return _math.log(1.0 + x)
    if f == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _price(item, inv):
    base, T, bf, bt, af, at = _MP[item]
    if inv < 10000:
        p = base + bt * base / _shape(bf, T, T) * _shape(bf, 10000 - inv, T)
    else:
        p = base - at * base / _shape(af, T, T) * _shape(af, inv - 10000, T)
    return max(1, int(round(p)))


def _get(o, k, d=None):
    try:
        return o[k]
    except Exception:
        return getattr(o, k, d)


def _cons(shops, step):
    """Town consumption of every product after the market of `step` (engine _town_consume)."""
    c = {}
    if step % 4 == 0:
        for sh in shops:
            prods = _SHOPS.get(sh, [])
            m = 2 if len(prods) == 1 else 1
            for it in prods:
                c[it] = c.get(it, 0) + m
    if step % 24 == 0:
        for it in _MP:
            if it != "FERTILIZER":
                c[it] = c.get(it, 0) + 1
    return c


def _sim(observation, market, shed0, me):
    """Cash change of our market list alone, engine rules (_process_market / _commit_unit); also our effect on the
    market inventory per item and the items we traded."""
    farm = _get(observation, "farms")[me]
    money = float(_get(farm, "money", 0))
    hires = int(_get(farm, "hires_today", 0) or 0)
    nland = len(list(_get(farm, "unlocked_quadrants", ["NW"]) or ["NW"])) - 1
    inv = {k: int(v) for k, v in dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {}).items()}
    inv0 = dict(inv)
    shed = {k: int(v) for k, v in dict(shed0).items()}
    cash = 0.0
    traded = set()
    for o in list(market)[:10]:
        if not isinstance(o, (list, tuple)) or not o:
            continue
        op = o[0]
        if op == "HIRE":
            c = _FIBS[min(59, hires)]
            if money >= c:
                money -= c
                cash -= c
                hires += 1
            continue
        if op == "BUY_LAND":
            if nland < len(_LAND) and money >= _LAND[nland]:
                money -= _LAND[nland]
                cash -= _LAND[nland]
                nland += 1
            continue
        if len(o) < 3:
            continue
        try:
            q = int(o[2])
        except Exception:
            continue
        item = o[1]
        for _ in range(max(0, q)):
            if op == "SELL":
                if item not in _MP or shed.get(item, 0) <= 0:
                    break
                p = _price(item, inv.get(item, 10000))
                shed[item] -= 1
                money += p
                cash += p
                traded.add(item)
                if p > 1:
                    inv[item] = inv.get(item, 10000) + 1
            elif op == "BUY_PRODUCT":
                if item not in ("WHEAT", "FERTILIZER"):
                    break
                p = _price(item, inv.get(item, 10000) - 1)
                if money < p or sum(shed.values()) >= 100:
                    break
                money -= p
                cash -= p
                traded.add(item)
                shed[item] = shed.get(item, 0) + 1
                inv[item] = inv.get(item, 10000) - 1
            elif op == "BUY_SEED":
                p = _SEED_COST.get(item)
                if p is None or money < p:
                    break
                money -= p
                cash -= p
            elif op == "BUY_ANIMAL":
                p = _ANIMAL_COST.get(item)
                if p is None or money < p or sum(shed.values()) >= 100:
                    break
                money -= p
                cash -= p
                shed[item] = shed.get(item, 0) + 1
            else:
                break
    delta = {k: inv[k] - inv0.get(k, 10000) for k in inv if inv[k] != inv0.get(k, 10000)}
    return cash, delta, traded, inv0


def _fd_counts():
    rep = _NS.get("_FD_REPORT") or {}
    return (int(rep.get("sells", 0)), int(rep.get("sold", 0)), int(rep.get("buys", 0)), int(rep.get("bought", 0)))


def _fd_eval(observation, mem, step, me):
    """FADE legs sit in the last order slot, so their fills are fixed by the next observation's wheat inventory:
    sell leg at s0: book before the sell = inv(s0 + 1) + town wheat use(s0) - x, revenue = sum price(book + k);
    buy leg at s1: book before the buy = inv(s1 + 1) + x, cost = sum price(book - k). A round is one sell leg and
    the buy leg of the next step; m = revenue / sold - cost / bought (per unit)."""
    inv_w = int(dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {}).get("WHEAT", 10000))
    keep = []
    for lg in mem.get("fd_legs") or []:
        if lg["step"] == step - 1:
            if lg["kind"] == "sell":
                inv_b = inv_w + lg["cons"] - lg["x"]
                rev = sum(_price("WHEAT", inv_b + k) for k in range(lg["x"]))
                mem["fd_round"] = {"s0": lg["step"], "rev": rev, "x": lg["x"]}
            else:
                inv_b = inv_w + lg["x"]
                cost = sum(_price("WHEAT", inv_b - k) for k in range(1, lg["x"] + 1))
                rd = mem.get("fd_round")
                if rd is not None and lg["step"] - rd["s0"] == 1:
                    m = rd["rev"] / max(1, rd["x"]) - cost / max(1, lg["x"])
                    mem["fd_round"] = None
                    if CFG.get("LOG"):
                        TEL.setdefault("fd_cycles", []).append((rd["s0"], round(rd["rev"] - cost), round(m, 2), True))
                    mem.setdefault("fd_ms", []).append(m)
                    last = mem["fd_ms"][-CFG["FG_K"]:]
                    if len(last) >= CFG["FG_K"] and sum(last) <= CFG["FG_MIN"] * len(last):
                        fst = (_NS.get("_FD_STATE") or {}).get(me)
                        if fst is not None and not fst.get("off"):
                            fst["off"] = True
                            TEL["fd_off_step"] = step
                            TEL["fd_off_ms"] = [round(v, 2) for v in last]
        elif lg["step"] >= step:
            keep.append(lg)
    mem["fd_legs"] = keep


_PB_SCHED = {327, 375, 419, 435, 487}


def _prebuy_hits(fl, step):
    """Rival buys TH+ one step before our tick buy (s0 - 1) and unwinds either with our tick sell (s0 + 1) or
    against our tick buy itself in a late slot (s0; the public fixed-step wheat buys at 327/375/419/435/487 are not
    counted, they unwind at s0 too but never trap)."""
    hits = 0
    for s0 in range(step - 2, step - 2 - 4 * CFG["WIN"], -4):
        if fl.get(s0 - 1, 0) <= -CFG["TH"] and (fl.get(s0 + 1, 0) >= CFG["TH"] or
                                                (fl.get(s0, 0) >= CFG["TH"] and (s0 - 1) not in _PB_SCHED)):
            hits += 1
    return hits


def _pickups(me, step, horizon):
    """Wheat the base route's units pick up from the shed in the next `horizon` steps (their feed)."""
    try:
        ns = _NS.get("_BASE_NS") or _NS
        chassis = ns["_IMPL"].chassis
        native = chassis.players.get(me)
        if not native or native.get("route") is None:
            return 0
        total = 0
        for t in range(step + 1, min(719, step + 1 + horizon)):
            tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
            a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
            for c in [a.get("farmer") or ["PASS"]] + list(a.get("hands") or []):
                if c and c[0] == "PICKUP" and len(c) >= 2 and c[1] == "WHEAT":
                    total += max(0, int(c[2]) if len(c) >= 3 else 1)
        return total
    except Exception:
        return 30


def _place_mid(market, order, lo):
    """Put order at an index in [lo, 8]: after the rival's slot-0/1 lift, before its slot-9 sell."""
    if len(market) <= 8:
        while len(market) < lo:
            market.append([])
        market.append(order)
        return True
    for i in range(lo, 9):
        if not market[i]:
            market[i] = order
            return True
    return False


def _place_last(market, order):
    if len(market) >= 10:
        slot = next((i for i, o in enumerate(market) if not o), None)
        if slot is None:
            return False
        market.pop(slot)
    while len(market) < 9:
        market.append([])
    market.append(order)
    return True


def _counter(observation, a, mem, step, me):
    """Sandwich fade: after the trap is confirmed, sell wheat in a middle slot at s % 4 == 0 (into the rival's slot-0
    lift, ahead of its slot-9 sell) and buy the lot back in the last slot of the next step."""
    market = [list(o) for o in (a.get("market") or []) if isinstance(o, (list, tuple))]
    live = [o for o in market if o]
    changed = None
    owned = int(mem.get("cf_owned", 0))
    if step > CFG["CF_UNTIL"] or not mem["cf_on"]:
        if owned > 0 and step <= 717:
            shed_w = int(_PROJECT(observation, dict(a, market=live))[0].get("WHEAT", 0))
            y = int(min(owned, shed_w))
            if y > 0 and len(live) < 10:
                market = live + [["SELL", "WHEAT", y]]
                changed = ("sell", y)
    elif step % 4 == mem.get("cf_phase", 0):
        shed_w = int(_PROJECT(observation, dict(a, market=live))[0].get("WHEAT", 0))
        pick = _pickups(me, step, CFG["CF_PICK"])
        cap = owned if (mem.get("cf_phase", 0) != 0 or not CFG["CF_SPARE0"]) else CFG["CF_X"]
        y = int(min(CFG["CF_X"], cap, shed_w - pick))
        if CFG.get("LOG"):
            TEL.setdefault("cf_log", []).append(("S", step, shed_w, pick, y, len(live)))
        if y >= CFG["CF_MIN_N"] and _place_mid(market, ["SELL", "WHEAT", y], CFG["CF_SLOT"]):
            changed = ("sell", y)
    elif step % 4 == 1 and step <= CFG["CF_UNTIL"] - 12:
        pshed, pinvs = _PROJECT(observation, dict(a, market=live))[:2]
        shed_w = int(pshed.get("WHEAT", 0))
        want = CFG["CF_X"] - owned
        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        farm = _get(observation, "farms")[me]
        quote = int(_get(_get(_get(observation, "market", {}) or {}, "prices", {}) or {}, "WHEAT", 40))
        cash = float(_get(farm, "money", 0)) - CFG["CF_RESERVE"]
        if CFG.get("LOG"):
            TEL.setdefault("cf_log", []).append(("B", step, shed_w, want, room, int(cash)))
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want < 10:
            want = 0
        if want > 0 and _place_last(market, ["BUY_PRODUCT", "WHEAT", want]):
            changed = ("buy", want)
    if changed is None:
        return a, None
    a = dict(a)
    a["market"] = market[:10]
    return a, changed


def agent(observation, configuration=None):
    try:
        step = int(_get(observation, "step", 0))
        me = int(_get(observation, "player", 0))
    except Exception:
        return _BASE(observation, configuration)
    mem = _MEM.get(me)
    if mem is None or step <= mem["last"]:
        mem = _MEM[me] = {"last": -1, "prev": None, "cyc": None, "cycles": [], "trap": False, "prebuy": False,
                          "cf_on": False, "cf_off": False, "cf_cyc": None, "cf_cycles": [], "cf_sold_step": None}
    mem["last"] = step
    tick_mem = None
    try:
        if CFG.get("FG"):
            _fd_eval(observation, mem, step, me)
    except Exception:
        pass
    try:
        tick_mem = _NS["_TICK_NS"]["_MEM"].get(me)
        money = float(_get(_get(observation, "farms")[me], "money", 0))
        prev = mem["prev"]
        mem["prev"] = None
        if prev is not None and prev["step"] == step - 1:
            dev = money - prev["money"] - prev["E"]
            inv_now = dict(_get(_get(observation, "market", {}) or {}, "inventory", {}) or {})
            cons = _cons(prev["shops"], prev["step"])
            clean = True
            for it in prev["traded"]:
                if it == "WHEAT":
                    continue
                rf = int(inv_now.get(it, 10000)) - prev["inv"].get(it, 10000) - prev["delta"].get(it, 0) + cons.get(it, 0)
                if rf != 0:
                    clean = False
                    break
            if CFG.get("LOG"):
                TEL["devs"].append((prev["step"], round(dev, 1), prev["tick"], prev["tsell"], prev.get("cf"), clean)
                                   + ((prev.get("mk"), prev.get("shed0")) if CFG.get("LOG", 0) >= 2 else ()))
            cf = prev.get("cf")
            if cf and cf[0] == "sell":
                mem["cf_cyc"] = {"s0": prev["step"], "dev": dev, "clean": clean}
                mem["cf_cyc_s0"] = prev["step"]
            elif cf and cf[0] == "buy" and mem["cf_cyc"] is not None and prev["step"] - mem["cf_cyc"]["s0"] <= 2:
                d = mem["cf_cyc"]["dev"] + dev
                ok = mem["cf_cyc"]["clean"] and clean
                mem["cf_cyc"] = None
                TEL.setdefault("cf_cycles", []).append((mem["cf_cyc_s0"], round(d), ok))
                if ok:
                    mem["cf_cycles"].append(d)
                last = mem["cf_cycles"][-CFG["CF_K"]:]
                if ok and len(last) >= CFG["CF_K"] and max(last) < CFG["CF_SPIKE"]:
                    mem["cf_on"] = False
                    mem["cf_off"] = True
                    TEL["cf_off_step"] = step
            if prev["tick"]:
                mem["cyc"] = {"s0": prev["step"], "dev": dev, "clean": clean}
            elif prev["tsell"] and mem["cyc"] is not None and mem["cyc"]["s0"] == prev["step"] - 1:
                d = mem["cyc"]["dev"] + dev
                ok = mem["cyc"]["clean"] and clean
                mem["cyc"] = None
                TEL["cycles"].append((prev["step"] - 1, round(d), ok))
                if ok:
                    mem["cycles"].append(d)
                last = mem["cycles"][-CFG["K"]:]
                bad = sum(1 for x in last if x <= -CFG["BAD"])
                if ok and not mem["trap"] and prev["step"] <= CFG["UNTIL"] and len(last) >= CFG["K"] and (
                        bad >= CFG["NB"] or (CFG["LOSS"] > 0 and sum(last) < -CFG["LOSS"])):
                    mem["trap"] = True
                    TEL["trap_step"] = step
                    if CFG["CF"] and not mem["cf_off"]:
                        mem["cf_on"] = True
                        mem["cf_phase"] = 0
        if CFG["PREBUY"] and not mem["prebuy"] and tick_mem is not None and step % 4 == 2:
            if _prebuy_hits(tick_mem.get("flow") or {}, step) >= CFG["HITS"]:
                mem["prebuy"] = True
                TEL["prebuy_step"] = step
                if CFG["CF"] and CFG["CF_PREBUY"] and not mem["cf_off"] and not mem["trap"]:
                    mem["cf_on"] = True
                    mem["cf_phase"] = 3
        if CFG["ACT"] and (mem["trap"] or mem["prebuy"]) and tick_mem is not None:
            tick_mem["rival"] = True
    except Exception:
        pass
    pend_before = (tick_mem or {}).get("pend") if tick_mem is not None else None
    fd0 = _fd_counts()
    a = _BASE(observation, configuration)
    cfd = None
    try:
        if mem.get("cf_owned", 0) > 0:
            shed_now = int((_get(_get(observation, "private"), "shed", {}) or {}).get("WHEAT", 0))
            mem["cf_owned"] = min(mem["cf_owned"], shed_now)
        if CFG["ACT"] and (mem["cf_on"] or mem.get("cf_owned", 0) > 0) and isinstance(a, dict):
            a, cfd = _counter(observation, a, mem, step, me)
            if cfd is not None:
                TEL["cf_" + cfd[0]] = TEL.get("cf_" + cfd[0], 0) + cfd[1]
                if cfd[0] == "sell":
                    mem["cf_sold_step"] = step
                    mem["cf_owned"] = max(0, mem.get("cf_owned", 0) - cfd[1])
                else:
                    mem["cf_owned"] = mem.get("cf_owned", 0) + cfd[1]
    except Exception:
        cfd = None
    try:
        if isinstance(a, dict):
            tick_mem = _NS["_TICK_NS"]["_MEM"].get(me) or {}
            pend = tick_mem.get("pend")
            tick = bool(pend and pend.get("step") == step)
            shed0 = _PROJECT(observation, dict(a, market=[]))[0]
            E, delta, traded, inv0 = _sim(observation, a.get("market") or [], shed0, me)
            shops = list(_get(_get(observation, "town", {}) or {}, "unlocked_shops", []) or [])
            if CFG.get("FG"):
                fd1 = _fd_counts()
                if fd1[0] > fd0[0] and fd1[1] > fd0[1] and step % 4 == 0:
                    mem.setdefault("fd_legs", []).append({"kind": "sell", "step": step, "x": fd1[1] - fd0[1],
                                                          "cons": int(_cons(shops, step).get("WHEAT", 0))})
                elif fd1[2] > fd0[2] and fd1[3] > fd0[3] and step % 4 == 1:
                    mem.setdefault("fd_legs", []).append({"kind": "buy", "step": step, "x": fd1[3] - fd0[3]})
            mem["prev"] = {"step": step, "money": float(_get(_get(observation, "farms")[me], "money", 0)), "E": E,
                           "delta": delta, "traded": traded, "inv": inv0, "shops": shops,
                           "tick": tick and pend_before is None, "tsell": pend_before is not None, "cf": cfd}
            if CFG.get("LOG", 0) >= 2:
                mem["prev"]["mk"] = [list(o) for o in (a.get("market") or [])]
                mem["prev"]["shed0"] = dict(shed0)
    except Exception:
        pass
    return a
'''
_PRE_TG_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order
_TG_NS = {"__name__": "tick_trap_guard", "_BASE": _PRE_TG_AGENT, "_PROJECT": _project, "_NS": globals()}
exec(compile(_TG_SRC, "tick_trap_guard", "exec"), _TG_NS)
_TG_AGENT = _TG_NS["agent"]


def agent(observation, configuration=None):
    return _TG_AGENT(observation, configuration)

# ---------------------------------------------------------------------------
# Team 42 GFADE layer (outermost, v12_6): generic fade of a rival's wheat churn at phases 1-3 (see gold/front/pack_v12_6.py).
_GF_CFG = {'XMAX': 90, 'MIN_N': 15, 'RESERVE': 1500.0, 'FROM': 240, 'FG_K': 4, 'FG_MIN': -1.2, 'HITS': 2, 'LOG': 0}
_GF_STATE = {}
_GF_REPORT = {"sells": 0, "sold": 0, "buys": 0, "bought": 0, "off": 0, "liquidated": 0, "rounds": 0}


def _gf_sched_steps():
    try:
        sched = list(_SCH_NS["CFG"]["SCHED"])
        lead = int(_SCH_NS["CFG"].get("LEAD", 1))
        return set(sched) | {s - lead for s in sched}
    except Exception:
        return {326, 327, 374, 375, 418, 419, 434, 435, 486, 487}


_GF_SCHED = _gf_sched_steps()


def _gf_rival_n(flow, step, phase):
    """Mean size of the rival's recent churn cycles at `phase` (buy MIN_N+ at s0 = phase mod 4, sell MIN_N+ at s0 + 1),
    over the last 4 such cycles before `step`; 0 unless at least 2 of them churned."""
    sizes = []
    s0 = step - ((step - phase) % 4)
    if s0 >= step:
        s0 -= 4
    for k in range(4):
        s = s0 - 4 * k
        b, s1 = flow.get(s, 0), flow.get(s + 1, 0)
        if b <= -_GF_CFG["MIN_N"] and s1 >= _GF_CFG["MIN_N"]:
            sizes.append(min(-b, s1))
    return sum(sizes) / len(sizes) if len(sizes) >= _GF_CFG["HITS"] else 0


def _gf_pick_phase(flow, step):
    best, best_n = None, 0
    for p in (1, 2, 3):
        n = _gf_rival_n(flow, step, p)
        if n > best_n:
            best, best_n = p, n
    return best, best_n


def _gf_eval(obs, st, seat):
    """Exact pricing of the last round's legs from this step's wheat inventory (see module doc)."""
    step = int(obs["step"])
    inv_w = int(dict(obs["market"].get("inventory", {}) or {}).get("WHEAT", 10000))
    price, cons = _TG_NS["_price"], _TG_NS["_cons"]
    keep = []
    for lg in st.get("legs", []):
        if lg["step"] == step - 1:
            shops = lg["shops"]
            if lg["kind"] == "sell":
                book = inv_w + int(cons(shops, lg["step"]).get("WHEAT", 0)) - lg["x"]
                rev = sum(price("WHEAT", book + k) for k in range(lg["x"]))
                st["round"] = {"s0": lg["step"], "rev": rev, "x": lg["x"]}
            else:
                book = inv_w + int(cons(shops, lg["step"]).get("WHEAT", 0)) + lg["x"]
                cost = sum(price("WHEAT", book - k) for k in range(1, lg["x"] + 1))
                rd = st.get("round")
                if rd is not None and lg["step"] - rd["s0"] == 1:
                    m = rd["rev"] / max(1, rd["x"]) - cost / max(1, lg["x"])
                    st["round"] = None
                    st.setdefault("ms", []).append(m)
                    _GF_REPORT["rounds"] += 1
                    if _GF_CFG.get("LOG"):
                        _GF_REPORT.setdefault("cycles", []).append((rd["s0"], round(rd["rev"] - cost), round(m, 2)))
                    last = st["ms"][-_GF_CFG["FG_K"]:]
                    if len(last) >= _GF_CFG["FG_K"] and sum(last) <= _GF_CFG["FG_MIN"] * len(last) and not st["off"]:
                        st["off"] = True
                        _GF_REPORT["off"] += 1
                        _GF_REPORT["off_step"] = step
                        _GF_REPORT["off_ms"] = [round(v, 2) for v in last]
        elif lg["step"] >= step:
            keep.append(lg)
    st["legs"] = keep


def _gfade(obs, action, st, seat, tick_mem):
    step = int(obs["step"])
    if not isinstance(action, dict) or step < _GF_CFG["FROM"] or step > 717:
        return action
    flow = (tick_mem or {}).get("flow") or {}
    market = [list(o) for o in (action.get("market") or []) if isinstance(o, (list, tuple))]
    live = [o for o in market if o]
    shops = list(obs["town"].get("unlocked_shops", []) or [])
    farm = obs["farms"][seat]
    money = float(farm.get("money", 0))
    quote = int(obs["market"]["prices"].get("WHEAT", 40))
    if st["off"]:
        if not st.get("liq") and step <= 716:
            st["liq"] = True
            try:
                shed_w = int(_project(obs, dict(action, market=live))[0].get("WHEAT", 0))
                y = int(min(_GF_CFG["XMAX"], shed_w - _fd_pickups(seat, step, 6)))
                if y >= 5 and _fd_place(market, ["SELL", "WHEAT", y]):
                    _GF_REPORT["liquidated"] += y
                    out = dict(action)
                    out["market"] = market[:10]
                    return out
            except Exception:
                pass
        return action
    if step in _GF_SCHED:
        return action
    try:
        if (_TG_NS["_MEM"].get(seat) or {}).get("cf_on"):
            return action
    except Exception:
        pass
    phase = step % 4
    p, n = _gf_pick_phase(flow, step)
    st["phase"] = p
    changed = False
    try:
        shed_w = int(_project(obs, dict(action, market=live))[0].get("WHEAT", 0))
    except Exception:
        return action
    if p is not None and phase == p and n > 0 and step <= 716:
        reserve = _fd_pickups(seat, step, 3)
        x = int(min(_GF_CFG["XMAX"], n, shed_w - reserve))
        if x >= 5 and _fd_place(market, ["SELL", "WHEAT", x]):
            st["sold"][step] = x
            st.setdefault("legs", []).append({"kind": "sell", "step": step, "x": x, "shops": shops})
            _GF_REPORT["sells"] += 1
            _GF_REPORT["sold"] += x
            changed = True
    elif (step - 1) in st["sold"] or (p is not None and phase == (p + 1) % 4 and n > 0):
        st["sold"].pop(step - 1, None)
        want = max(0, _GF_CFG["XMAX"] + _fd_pickups(seat, step, 4) - shed_w)
        pshed, pinvs = _project(obs, dict(action, market=live))[:2]
        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        cash = money - _GF_CFG["RESERVE"]
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want >= 5 and _fd_place(market, ["BUY_PRODUCT", "WHEAT", want]):
            st.setdefault("legs", []).append({"kind": "buy", "step": step, "x": want, "shops": shops})
            _GF_REPORT["buys"] += 1
            _GF_REPORT["bought"] += want
            changed = True
    if not changed:
        return action
    out = dict(action)
    out["market"] = market[:10]
    return out


_PRE_GF_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    try:
        step = int(observation["step"])
        seat = int(observation["player"])
        st = _GF_STATE.get(seat)
        if st is None or step <= st["step"]:
            st = _GF_STATE[seat] = {"step": -1, "sold": {}, "legs": [], "off": False, "phase": None, "round": None}
        st["step"] = step
        tick_mem = (_TICK_NS.get("_MEM") or {}).get(seat)
        try:
            _gf_eval(observation, st, seat)
        except Exception:
            pass
        # hold the TICK layer off while a phase-3 churner is being faded (its buy-back needs the shed room at phase 0)
        if tick_mem is not None and not st["off"] and step >= _GF_CFG["FROM"]:
            flow = tick_mem.get("flow") or {}
            if _gf_rival_n(flow, step, 3) > 0:
                tick_mem["rival"] = True
                _GF_REPORT["tick_holds"] = _GF_REPORT.get("tick_holds", 0) + 1
    except Exception:
        st, tick_mem = None, None
    action = _PRE_GF_AGENT(observation, configuration)
    if st is None:
        return action
    try:
        return _gfade(observation, action, st, seat, tick_mem)
    except Exception:
        return action

# ---------------------------------------------------------------------------
# Team 42 layer (2026-09-27, v12_8): end-of-day pickup deferral.
# At the last step of a day the engine drops every carried inventory into the shed and destroys whatever
# does not fit under the 100-unit cap. When this turn's actions would leave more than 100 units in the shed
# plus the units' hands (engine rules, _project above), this turn's HARVEST and COLLECT_FERTILIZER actions
# are turned into PASS, last unit first, until the projection fits (eod2: only animal harvests and
# tomato / strawberry harvests with room to grow and no rot before a later visit; never fertilizer or one-shot crops). The produce stays on the tile or the
# animal and is picked up on a later day instead of being destroyed tonight. Nothing else changes.
def _cg_units(action):
    return [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])


def _cg_total(observation, action):
    shed, invs, _farm = _project(observation, action)
    return sum(v for v in shed.values() if v > 0) + sum(v for inv in invs for v in inv.values() if v > 0)


def _cg_eod_defer(observation, action):
    try:
        step = int(_g(observation, "step", 0))
        if step % 24 != 23 or step >= 718 or not isinstance(action, dict):
            return action
        if _cg_total(observation, action) <= _CAP:
            return action
        units = _cg_units(action)
        out = dict(action)
        farm = _g(observation, "farms")[int(_g(observation, "player", 0))]
        pos = [tuple(_g(farm, "farmer"))] + [tuple(h) for h in _g(farm, "hands", [])]
        tiles = _g(farm, "tiles")
        for idx in range(min(len(units), len(pos)) - 1, -1, -1):
            act = units[idx]
            if not (isinstance(act, list) and act and act[0] == "HARVEST"):
                continue
            x, y = pos[idx]
            tile = tiles[y][x]
            if not (isinstance(tile, dict) or hasattr(tile, "keys")):
                continue
            if _g(tile, "animal"):
                held = int(_g(tile, "yield_units", 0))
                if held + 2 > {"GOOSE": 4, "COW": 6, "SHEEP": 6}.get(_g(tile, "animal"), 0):
                    continue   # tomorrow's production would hit the cap
            elif _g(tile, "crop") in ("TOMATO", "STRAWBERRY"):
                if int(_g(tile, "yield_units", 0)) + 2 > 4 or 0 <= int(_g(tile, "max_lifespan_step", -1)) <= step + 48:
                    continue   # would cap or start rotting before a later visit
            else:
                continue       # one-shot crops die a day after their last watering window
            units[idx] = ["PASS"]
            out["farmer"], out["hands"] = units[0], units[1:]
            if _cg_total(observation, out) <= _CAP:
                break
        return out
    except Exception:
        return action


_PRE_CG_EOD_AGENT = globals().pop("agent")   # pop first: the loader takes the last callable in module order


def agent(observation, configuration=None):
    return _cg_eod_defer(observation, _PRE_CG_EOD_AGENT(observation, configuration))
