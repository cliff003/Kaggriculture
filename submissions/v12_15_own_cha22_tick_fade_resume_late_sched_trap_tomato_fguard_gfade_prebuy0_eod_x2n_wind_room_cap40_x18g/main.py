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

# x18g (2026-09-28, research/carrera/patch_x18g.py): the embedded cha22 source also carries the 18-tomato V219 extension, enabled only with 4+ pizza shops / farmers markets open on day 18.
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
    'ck^KHuz7S0OPRG&;Gz3iDz24z(&JFk-M_K%V#xq2Asy`RXs2;RmH?h;#kJ<q)^X*qhWRIAv+Z+nmD)dfQ$0F?5{nqZIl}d7v1D8qS5M1EaaFX9>k3{1&YFtd'
    'hxOjQxv`%!&-!_x0HLRj)g}+5J&FOmHMh7bu~F%)MJPVD_-gF-ka1Ls8?;WSoo>%Q6($mh%NB1rs-7XcS57EFmwa_xIjSCGXKynYvFsA9d`=&eIdg}2;+^im'
    'lJ97eLl0DT1$rOf@8`<UyWyzI5%E-=(zK_;<O{0OKwjDC@{3efxy+*<&e%f{ew_d{XkFG2yH^ASFHXJ}1dn(VT~<*nTI0^CGtwga>1_}1&k8zAvHT+1`4Wev'
    '>$WiGqu2(+i+e1im@|q&$ZO~#;Ib^!0<kpL3P)f^VPg`TO9zwSXZbOQET`l>*ur?AIW#d@HK=p(x(IG=ghTkSVjTd@mKMvn2a<*7xuOX_DHyjAMdK%^WaNk7'
    'qb&?uVu6#yBH<(hKthtLp`rlPJ<oi>gSfxBND*@wLCW98eZF`V8|@5<>Rj+PbNDHf%N$nVpOa6SyZBN^Nkvq13{J#E8XHEjR47negkC)Kq@Jl&54LJmDjXJH'
    '_cet(c;xBMW{&p$`fH1X4xssZ>-Yecg66^2@w-Yb!`p;ZkZ>4zSAA?(b(sVVr+Hiue(I5t{nw#emchAs5pr=UzcA~HQx%aj6;t70PIx-R^$^_XQnS*cc^@S)'
    'bT`B!^+}_CO-T(i`_=7tm7NUV9zty{<(9eE*TD>1$`uRdz3niI%BZ9|Uq398I!Qjr6->o0deJisb%>UHNXPVxNOE)u2^-N23tcN2)3PK`>X^79B}5YK+IR12'
    'dc$mdYAfp)b0hnx#=_c58Id}udIvY5cWB$x*t+ywz|1};zxpLQjTs&;jy(V6x{aaTq<e$P1Tx6cFP`!EMACU5cnG&p44I~AK9G(i#oT_P7*o69<?wE>O?CoG'
    'vBiZ_8Dv%?zJX0K==vu1s}EnA`&);CgLpSQwh^w>9gT_+pl!>l^DQgD=t^d&1VwcLR4BY=V@|waeK)NU?JBmY_>En;B|3YZn^^FAeRQ20O)UPV815S9%;;LS'
    'RHtjsGW=x&Z#bh<Rdl&oCXmq+sx=8}(dA|t{<MMjnsGI{(kv1f&f#of)X%&NzOlL-DoTq^b}_eT=3v6&zl*sgdR{WkTqwzXaCaFcyEo^8Ys>PO_ue$4ZHiT$'
    '*DC3VB~N^G>Cz+5gNSoj41>cZoXIhKqU636Z(T?WD=a$X6x!>mV|wU&%A*nqHhAAxuB~y8ML$}cJ%_HY=D1{SD$h%B`!;R0h}j34ELBIh1H0!~(}qS$%k%T4'
    'HA7tUgDqXbeD|*A;|HjOL?SIS2o47rkF4TqQrt=SFq68A6*U)>Y49hhmW)(MQ+80-Q70ikAC(phobiE>B40G9>ti1b2HPDeU0R5zh)7eXxIo%TDMTkK(NQC+'
    'fF4YH+#>@I5-oygTb>ubRCMgYr_q)7d~`N+lzb(JxM=DWgce}bw((jHx7RaB34ShARpEpg;qI#gS~eP^7jCCd7kVn*;KW|K$OgJjd@_kZxFB8&>v-l9%+=vU'
    '>q*qdf$-400_7FedkQ|x%5~ljuk&IY%tW#IX79K%U1XX$kru+r7nK!icjyq<a)dRaJhiZ)A-Ms?Nxm!u3pLHZO$jfFi&UB(ONAs+rMY6c5n6v!x@B{IT$#OT'
    '>f#VvY(wnKp_SMZpQ5^2p4ZEI<}_+XPH-w$4CgGMQA52szJvs*%h5|vw7EP8O&v89@v?y=dImR6S=523aVtatX<%S6lvcQd&Ed*gQ&?BprByIDMrV}OoCLB6'
    '@>0{fikHvgG@;oA++D`$cL6pR=&0<Ly8!*eH|C5rqvedQ&^=3v5T-0CaNS^bZ{Zwv<c-oe#c;-yfFw2o0nqT|k4nWL0zzc=5T>QH!YSMj?MY!eTiH^Cldp@b'
    'GF3s5W{#vuaV=LW<VwX{sgx@%<Vs6|0f;F#tP<DBE?}L~@&*b=c)Lmmhhp$`Vi#9)phAl_OQxLTEpKQwhf51hdTgTpbV|EW8o_hHh-iF*<@F;<<xr35b3G${'
    '2Mu|md)yycdciqdK?C>_Wy>n9@P4XnMmr2bn^Wps=+vdBtRKOET6{H7pv^UM{Ntno#(`4Ea>dmt<5iGmsm7=>H4@Nrr67+w;P>Xw(L^Vum~T0GyB*q^LGP)7'
    'LSTieFJ;0$2;@VYMHnL*OzJAMOfCVbhE6v@0TLyRsE2`5afhw$n3S2rw*<@F3|y8;!hp7(fThOhHKjNo+9d#MY2G*%cS$eg3gW<~@V^HZfN;wXDXN6wU5Hes'
    '>$F%4*Fu}^1<m8GZj&jN2)synDMFL*?rCvqft)rZZgqc55PZvI5%Lfrf{>yU#JPlbAwfCEv@{>Wq>RR#wYY}3rZL{)QX!EwWbK5JpUtNFD>R;I%q^LLNku6k'
    'l9rcp>;M53O$b`Wr58U1rjz7Vg)Aw~RHoE0XR}I=PC%856&t{LV4drSl;iF2m6d7D+-A0`pEBjeLLrwqc~hwzWy(wVyj!iFR5Im-Lg6lGZF)l_FjAZO^ro@}'
    'oh<_F?XBbEDm;T!m*NE)h4yR5Tc2K4j*q`!Ie2kU*{>dE%Byi4qW-82(JbIw(Dzw1M{hmmk4%b*Rj1qQDuqD9x@B9YjQ{4ub(-Yu&y?lDKUd6Uh`llW1?Hj8'
    '=psE6S_yL6C6t+R@SMw#XwQ`C&)t-DMUVA`g=&B6RrOePlb0>!ixsiPDaClU+UTATCr;AK;*6fdRH|r41lv-ATwx=nfy=NsG!`0!uwxyd5V`(r-4ZPZALZ%K'
    'P)oW~KfqRK^eM6O;%hMJ<}4EHA!}O{in$eNblFT6=CR1;H}rbSM#hyqY9f<moNPSP!3(wFg*#e8H}-ssFZBo~Y7sff&2_MNEO~T7Y+lI?D(yOS3sI|Q#IL}n'
    '-lB6jB42FB?aJ^?ZSP3<qWZY?+*Vn4FG2I{f|kfOnp7m!$!{@oltBdPB^-Y`X4=VUvDonsmA*n8myUcCNoVkTU0y3263|iRNZ$E?0S}H@$gG%}U((D6P0GzK'
    '{g@@vlk4CC0bkSHh4P6E9u&fWxCnEji^qz1dxEd%yRsr~EG!m2(Sx6)_JPmA$ByIUwIx=7Lc$se+Fn6+rcSpZBUyE+#mnzfxK%|iUHK}Qo0e#_%<x2?dCo?b'
    'lmM-P+ddzw?Wcqjz36(tbj3cUh8a2ohYl&w0Sj_qNaK_8{cs>9Ml0d~wD7V#=_Lqqdd9F@=XXhW21AJui-h|eU6aEHVNwZ{giwqS5;f^kJlflS_u(j_^9qQK'
    'NCK185deM73+0tzk-&ao5)K-2=qTm4>u5T%oFOBUw->Zz1T;mg=#}A`vtHiJ9P`(QSWEcEsRkn^FB4^ff|rNNO~t71I;jX<G%CEm>uHif77hhqATo+HNubp%'
    'zYk~J2u(wlzfHkX-$e~0C<LJuOXHG0o8!)Y9d|b-De#~YJkdg*%NNZJ-0v)jn6qRVP)InBFEQ0L?@Uz3B*VA38X;-|!Y&8usmve`+>zQWlmj%Pn-Jkv2%m>='
    'GLaZL`4efx0sNi4-B<?`J49Auj~&s0dznvWC^s|(RZl?I@HCGPhFy@yItq{jGU?orBMz@&2$^)IY7w6rd|LnKW5h-eOKB|_6V-FV15de;^=E2b|Fl&@vnqk2'
    '_pX@#pD|!CMhXM%uK5`ED5WDb>%{jm3Rrb@G0*9o%+##BcN|0~B>S0783(-~=C$@P%2Wiq$Wv<SKJ`HlbR|k&C{BrqAxlyv)@3bA+X=$2(aj)wSJYISEb3jG'
    'n8zlsT2A$`i4C4jt5nJdH?xOFXxeUXl8S?^)j3hO=9o%T)B;NpNw2jKCO#cn#S;29*=0GaQRfm9=0>PP@9<W0u{w$j<(G7Sym?=DgiOZ{2{aV4N!0nfGzmg5'
    '%&_M^bb$JP@SJHfWCO{t!@vlNM^+m5A8*&9&hCw;oSxT;cMGRvwhHY->WL8b05KvxS24poacXf9Irla~whUttHBqfw?W^z}pvWrci#g>7F5lkeG=qqK>Iy{}'
    'V|mORs|4alOq3}Lu3XQ8c4j^#sH1TgHIA4Db?(2&VG*+NwZ3ZEvUs=8O3sZWfJM@JVVFV8o(EZb>auE`5GSR0L+m-ns-y5}@D@u9pbF3V<G`PQlTrhKHmy)_'
    'WHh-#fLvMpQ0BJv2ctC?E4z|gO(?r&rtShLdeFSaRebvHvq%m3i1wRf^j2=3b@4*&Y*@E<>v2n8B~Xz2{qa;sA!ZT&H)cahfu&q>dLAtF7x3$_H#T9{u82`n'
    'qHsOr$7{@~*X+e(j>()<GC{mhQYc+StKhs9n3p}c20H>cDKk}gfA5^+7yz-Xpt9~wY$T>KivcN1Cr^~^5>iz40y0J$1O5A7gH%$Gvh_NJr{uEB^zRD&yGsAA'
    'iGP>r%`$ymrjpBMBUh(Mg262-^lpW|uTWY3ca`3(($`fgxoS34D)aR1glO-$#_UpA{GD4$>@e8Xf7UDPL$qJHSg)|uztgV-q!@)HVh03XRw$}Q;@ywV{d&s$'
    ';`*>6l66!LIg^r@R|H0pS0EQGZ{i`BoC7azLX-n^f|oqGv%IN_VJY$E&AY@oCZNeY$mp#%Q#|ugPmc9xlu8E_T0htaJm7VJ5&<iyj2><q*`qVX&5fy$WAtlS'
    'ad`UYxQ9$R5gQiYy%fSYC3zug>C}^u#GXo_JZRsKgbzH9qd%~(`a!47a_X)Im29S_7Yz9~NhTN4VJY8H0-!W6lj4UtE4oxfoOcNuDcT`})cR7_jt287g-Yzh'
    '^PWXWy9yKmg=IPBY4WYQo&`z9X$s4Ptc1o~4{X4!UW|vBOX*ypZdl_@c`Zr3wke;qw&(GstgXzy@Re%FjG6~dbxPee9uH8(dYe`Vc1lhnX;4OYgA|>azyT&^'
    'Vtu)VV}&e3mE+33K(m59RpscJlAQ3fl%wZGH0Q7`d$j^dT(4Xj<@kw`99xCu$SIM#dA@FsP)B1po;V455N2h36Q3_}1yT|wyd5hyexxTR7wpTFlaprF^^5Yt'
    '*Z68y_gySyc}jY%cA&$eM9j$-f;BDuiUj>?grrE%XgFVDw8=&gVxoL-oFTkiqU|rvX%&v8P7aUL7+%HeB%egn_aIdoIWtPMkOnRx#(ZxNqGwvFF4bBzmM2-z'
    'CZ10MZj-fBu53s+HmQM?hwn<oS7qLw=QJ7e*cqM?772K;*6uou(ZrEyU3wU4in#&ixvj^>Hq0V<9FHRVIl7hIurh0f2&|La+VjSix{^dh3dtO!kAuV1A`=Ay'
    '3>_x$$#bj{a}6E8J$5+!7jNzoRVZf;Fx%cPWwAVYv$a$Gq_SGZlDj_m+6uh2B<gobIF%`{$_xbp#FD>D2UZ%IdizN3t)rv;FU{H>eB8CfnE~i!<?~VHc<-Qc'
    'SQ9R(q(jFc=AzgDJvtLqN^#gYTyW@601M11W^0)TE?)BAJFqO*{aCjiln)vPNGFr<+$KBUHm%~~VmZ(=N{ck#K#@eXEg=to+~qLsuyi7Q{`FJQk?AesI+D90'
    'u#*V@(yoB0mjg-NkX0}*j#Vdp$TI`ctda?+T#<C+1G}pzG%**%X!4bIDtBZsI2dfT892Wa+!0iXkO+le(<_TV#B4n+)=S<%k)Q*$$3x!}o(nBt0YjC=x7b3U'
    ';zC5jTnse(c#3ZsbrIyxOv>{ZF3H3T2Zm}Pab`G#qzI5@m{}6+D2}<%i$=H)k*~2XiPw^eC53%Nff*smG50W`@^@pML=Tc<otTZ&1>?UZt@LIdDyX7zX$Ixe'
    '%>Ps_&9GdWNtR19ESF}=^%;~)GmYE~$)y>TOEXOWnTN@x=EsHN-^hp&Y$JzKVoXa!0qy+r92%Su+e((<)A&Gk^FciDXC0qQK_}11{%wBv6I%XXFJF(fJR0jF'
    'l%Q>oMm>km#&t0lDJB+^IX`m7f#=}~6p@9sSTHG-hrBu-LjyRH${&Mz=#Ivms8l#ID4{2we|0ZxJc~t?G%%Og5HsUo&Nn^R1kfWaN%-CN){(U+f3Rj~iG&UC'
    'f_q0V)cOps`_7fPWHNFpl6T*Dw=M9@U}kQa3zdEduSv5to@C0%yAfMBgNdUt(Gc&=$>N}-(ye_sG`>4>#7^FY+dFS^8d!uL0To1X@g0G%Hg=lwtf7`V9D}|j'
    'de}}U0hX+d-$m*QOgc^~DPbXOb^%BG5J}chh!B*Lx?xJAp?*w*y%%kJF#WV=+I@8KL!OiiU&e<f9q?R7`_q!w+lzzZ>zeHzd<z-$Dngb+Vy!y6ij;vq8*&{b'
    '?KagzOwovLG^KcaPbssF7C#yU{9%wiM~_MuoxCX^<oXgkN-+tlWZ+QEaSLWbB(&ytR6o{LWVXE4MEe+nk<5&`S1~{&pAIHOI4uZ`{L_+r{b*@1nHrHGL)A1+'
    'Fc^D^HcZH85Yh&+4~fxYK}AtoI5u(bSGYJ&LV5gFp+#GuW=gyv$%F>)+BPC}<j{!89ru3meHf~e@O;Z^N+Kzr7&Be$a}ZsPiPwwK`|Kh^A4rl|bboZ9RII4x'
    'rV9lHOiM}6CFHrdIu}j%9_MDWdXcc_SfYUu6GGt8{du6@dRIZXu9Z9=*S&UoJfJ%Wuuj0LOf#8FF*w>Qkgk{MZtdWDRGkS_#J#17B{5LSr@VmxwC`f8PQPS8'
    '<Rb_L_NPvPb>ugTm@PaT5aUoxJjX)dA$Bc-m6<j8Btum-vL?@w|MSTfnNIjOHswfGX@WO3U@v;lfB>#9+Q9l$T+X$`1yvS`K+~v2vAc+@8H-B55dqtT;}!9T'
    '^xLXPZa#?>4K7d~+MuIUyTp6H0qBxEMjNp?F$d$&isub_{=5`3qqDL#5zZG`Nj9y}_t0G1j5t@5Mw>hmS;h$TGk##cnIwKn2PNI#YTB{T!*nz1Ot+Zvg0S*<'
    'Tl^LaDVNY0Kvm*vXkPU$EMf9fdYvk^rwi=4dm#!vG3L*fgE*btMAV?*w&ZC!9mCCn4C&NJFQw~d;qQwK6+;b6K<&eEB}HgR(IVv)g@H$fn3VC+!43^{qFjis'
    'dU7w~RxHS6rUR=dW&BqJ_{liKJM$sqK|U=Wjo@XmF@<qc2pbv(0fh#_EK4Fp<&wM^MQO+Kh1|Z9D_)_IlaFfiO5A{}ug<X>aCwB9((&m<Z=#i=EAV7`vBRr!'
    'k;i~LYibs)bv`3&rJS7A&fNQ!IQtr$d@bAs3V_U>8j_Tev`KvEpigDvTgQL0GSdCfgcTnj_3K!sF26T4pB{$f)A4LQ@EN6D=+-1nv$$UhYWK1?g$1u#P&!l4'
    '!~<ZlnMuP%QI~idMm+FxZ@bdmKCWyX$QLIE)oSg{UWI>)Kul4WplQ+QrQ))@TD2rIBLEw5G094C`)C6!ShZ}#gnL8@*H)Lf98>|+QE*YIkqng2Rt8ly;s;y5'
    '`rH9&Sd4=T72%+Cbdb}i@NFe(D5T8EeAzlaY@XDrm^wu&dRQP19XUX|`YCg;xBrgxs7)*S=~K13A36Fap$L{HjseYKG4xWbK7d?&KO)+>b)^D@j+cjIY;i-a'
    'g&U&7!EYG+e4HoB36A~*4L}{hn@d^h6HVY-Y3i4gO^{q*SC{3}ojee7;`Dla>?627M_m}xQ|D}*j($!EZw~4QIhH8Pgx~W<^U<K5klGvCoFR6MMgp*y4@Cm#'
    'qdoFQFjg`LRrpRfzOd{eqCXtMK>QZEhMf|fpnoK(4>`^Ef<1^ZZ9arz<oZW~oDj~dl0Puc$=4XGUA3Sm#6(HG33lrw|0W(z3OKRU2($Z~b|gJTFAPy7&u7>Z'
    '44PO}#1zQdj#%_IHH#lY&R2O?*`IG2{0sM&tAicNjhuMF_<hGZ5>9mJFvV@2F)wuVh>LP|-@BI)Y*oeFu*uPS%583{4MOE8pKtdZdzht@qrppYzqpQ8u#KQO'
    'Krkqam+U}LYL4@qCJ)mb*~*QroY+ZGW(nS>6fgD^A9mR9ZiaX1ROfN|#x0O$W{zUc#8}gFoPMgbxHz&IBm^OyCS4&&i786hvr&!7I3UW!zPu8oSf@>zoeOs~'
    'bX{Y&H@@k3ml@xvU3tc~=VBBOru;fNbDV*^&kgr{c=JYP6yiI4f@MP)t>SPzM-~O=K1DQ<h{Tqc<lzmd3(L)ut^G=L_Xgh|Zq@caR+{^jtsQGyrZx9r0c!#u'
    'cEW{DJ{%n#S58iXf?!$oCQZDd0q-&*iUqC3cYcQONhCN#=qfS0Oq!lkYgdk<r*af5h{-Cj4J`_ZCVgpjRSJMjYk6%s;XGobhkx2&2yxlVY-lcH1&LS^trAL$'
    'lp<phTrRRjLe-Ab!dZdgQ*?Jc;&OYJp3-RA1*TJ$H!T<=dfz6drQ(eYO$(4Kn3)5d`EFC8YsD2uSvYSAVByaIAV>;iC4kGTYXALDoE@zw2Wf?3tVq;#+c0a-'
    'yiPVWgyDe|;!)4cH*K>_Pbw@X9^bWtL*%saax}WB4C4WLN>a?;InH%_Pq*N3(ot~;FPwX{xK<J-67qDyZuZoZd+|-YMvy1n`hzU#&C9js*$s%hwdP)}a?pJ9'
    'S4y~_Ov)xs<u0!+5u48u3o#VU>cS90ddJ>Qm@+HPH`U|4zp96+@q{H)OFstfFnN+l^YGyI-0YOVc0q!)G(I@?bUCNI`IByb>a(Ix0i`})BZg}IMGN!=PK$$P'
    'k<oDmm`sLn_vb?gd?{Yt+~g!V?U;k9Exb$YUIBIH_`^1O*+Nqc3(5>aS(oE5+tQ&V5}&riyCW*RnYKs5nTgDM^L-{79pQ^GG^bOF;1Xdc>=m+Z@$Td)W=Byu'
    'oLJWpin<;$CIi6*NU1=zCEzyuZp5ht0Xjx|_UxO}L4h(eCZ$WxBc*XDw&#6R&u7Y0g+z7zL3q$AVadiwHqtr*?fK3~B%zHiC|YEpxI<cA9vxmY<X6#IoDcDv'
    'r0MeKjZ#81VX$+TWYZ;F8!cpBpxU4l&%xyf$DD75jyJ;++ZKTW`bILe(3Fx0{<0)ufm6qi4P659m7LsRT_`#F`3<BQEL3!WIta)lxW$}oZ>|`1Q+LOBHIl`b'
    'Oo-}@xF_4HbHS;CN-vTqs3N)9BRmw@ry?>0lYkuCDN&gcm^SAGuuynr0Fmaaj&3M#a6%&wb3CL#yw?-KBOY;WT~O{;WDv!5!UG|Y$<wr<*5t^kkoNSO&lzrl'
    'OF(B<l}khc=4z(7u5C&2yZ9L#eWFB(i8r|;5r6WjtK3h{=NvR0Ipr~$L{MeAreCoh_pv}9;>{!w0Lf`FO*H|9wQujt<l;P6sgh3ixu20kBN1Bz#337)Z0`oq'
    'FtNMfr`F`2XyFtwqwr6?Bk^!oW@b_;k)QB@qMjczjGbI_5_)G9axu*1I}Tg43K2g=#2mcWzYz}gr0h6aA>9`P+D|t0k$QQayM+E-63@W1;r7F0QO{;to;~cG'
    'xHk?au`_eo3~5J4&Tt2F1(on_1d1fvw!u~wx$dYOOxy!v+$wpSp+*gA5|miHf$V=o=a2Yk;xjw_00mf}4-8bE7J-_~iYk6L#th6kS{a-fMa=|F;GF27$Gk`P'
    '`#mC%h3BJ>w*-<Cg74kTgF@o)4Y(p1RgV{Tac#D9J@AI)`sVB1MMH*Voc6qy-2-ijjNci0J!482i@4gl4Ghq7dl<nWBVx-&Z`^j_p}4kgyzV*I%#+xdkM1z#'
    'bioYHc!8P2w~6YZww#)&JMOd7M8Cav%H6&5`eoS<x;2+>d47%;XgkB_54$n<zyEPBkYpgBM`z?-SrIu;a45G9=z27ns284Ew(r10X(?x9_6qO>Go^r6c;V+o'
    'dTKd6@2ZKtg;yE>=Ma`t`IgUo;~ih~tMHQUu~bES-f2d?)Jm4_;H^v$9N@5!jKfkKhcnQZodhI`^Mx1^65kjWD~N?mO&nmcTu8#ARCqWRh55yYW3h}_=t+?S'
    'Op2vMREmExC@b+n!HZjm3Ahv)7m<%yXN^QO781}910KVolt7OJ3>FxJ%I>b-eoFHTrGGRaQ+bp2aP*N#W{P5|^ze~b{^OCL%~pLN3Mu@s^zRP@kwMF@rxT;_'
    ';29G1@F63TMh+-^cPB&{T`kvqy<e>!<CTHp?VG*B-AZ$JYwr+VuFe;fw{8VbsScbhwvjWgb4D$sXI(>a(&bTZTnA1gERHw6%`i?gWx3v6$BXzs;j^|RUK_K?'
    '#fBp)C~tED@jQ<&vx)6`rwmmu4KK4G;fy&WrAo1Yl_FJ&g(;P2#>{Bi#baZ~ft8dzJ#?KlQvfT~aG8`hGvnrw*Uz)#N4X?5%cF)xYQ~0T6k={;os<;W3Bz!0'
    'JU41F&(Rq0j*jqbFl1vRk22phW@n93NHMwAT(&Fn=p1<^*f<EnsB-9awJ-b-W6aFVyzY6ZqK=Fx-_65Eahw3~&T?(+ZG5dY*)S0fA-w0!G6wY-e3}t&_X_-O'
    'uOQ#l_(g4|q2~)^WQ`4|pa&=kfNIvwXePdWG0;Ere41$h0ST4op$P(01OBIJvwU;C#bxIR*leT*;GWkBDXUZ1c?`*5wkIN~Px`-yWIhqe|Hs~&H@9(Q`J(^7'
    'i1!`JZ1)99C{S3qf-FYRGHokb7JVt%o^A#L4FW|GLlA(lh+=DWKl?jdu9Z~)DcRjO;`PK>L{(PqdGf5kW9F_79X6lqWAd@;uW&*<{2YU#*!v}pV`o1tMt2}q'
    'BW9<AlwdZ`+1(6TPD;5m=uhxK-1ToWOobJ#Ci86E_uM(g{f8+g2p?m@?*4dmo0)A!u{1Eq5Sp3<9N$lp2*YH?P>kMO1}*2^MBX;*;rAv`^?nk@Lc>Hz)Y4k0'
    'G@0PWc0;Ljm%u>dK*&P_{%u&U_?X{yG>QH-npH2Cb{a?ONhphBw*Vi?{apGQtiVY((8t5vw_&OimCZ^y@Wr0TA9R}i{Wv)hg_YR}d#GMaTU)(y>%A(k_iBTB'
    '(W=?U#jszKee=qH>d{}G{aP9|eT@#U54^$2fd5{3CxzcXml_Ck75_MaJ6BTpY&Wcg33yW8ucpharx0#k<WREXC2SF}&dx;!2X@7x-+}>*`_Td>YAjp)3Oka}'
    'Ei;)iu*Hp}I)lE_$L8>m!Zy|JUi?tIwWpCWUPhkvGV(OhQNzn>qia!Wa&fcE-vcG5!jLELfE&M7T?CP?%zYvk4~TQO9ojF|53wjsq7UJIC<r9W1@;#2KbX%P'
    '5~hY`;cyLV445<2Z03QKU`8m0hKu<C0QB(kwyU%Y)Sx26LbZZWk>zBHa0g|5Subx45>*j#bs`!ADPv1pD*cQcH517u);E-uNgNT^S8?y^h+iyo=;Gb@S#K5N'
    'pv0kYX=L=(w9A%(xE0)9@rIPE$QtA%%Z;=za<F){YUa-hb<AhiMN*)PB8dr;UGZZrs!KaTLv8$bY#^~kTXT)`v51CKPM`rt8R|pD3~v&0tBlSt_ag@bQT|4t'
    '4TEd~m+>@F)sf~Kz8_!`UZ5a1qv0@{=<|9MeSnEVCDVK~%OY9@nApKQqg<e*30k7vUuDap^TDK|1#$~6<UyjBR}EtV%f>6cmglVfx8gc^#sAw_ic}}#*rcPJ'
    'Z(J{R^%1oTHG;0!sUeSg3-|=<DP7|2dOiTT{Tn(gNd4%L?xZ)qBJZmC;t2b3OQ7a3;fz}(_HJs!&~5fvN~5r)I0_?G+3+jyZ61Kd$DK0qjq{~pNEpt9A09^*'
    'm`W!Pm$JB|a)=#H3AaOzGF(&s#?4zQG0REH<$ZJ&eC2e;xace{;U)DTE$9J$?6yx9TXiwYAUar0&L_w-uhWO0=^W!*`WbhEC@Q8>92DtsxqK2?IPBBT2CRZ&'
    '6A~f|^F>B!P23=9TEfhNS(l9f%Tkiljc!Tw^?ZZD&)5Y6xguCA-qcCT;gm03wIju2K^CVFaZLRGn)|yQ%uqwH3p1sxUfk4y?#!l>1*HtULO+4U40F6-R?cxY'
    'g@+%e@c#)`V>H!2k5ID@KUNq<7ky~DUV@ltLTDgUQWHaj3Y484w9S5}U>NYX_~Ow3sUtn%{?bOmzptmOIn7TGRrcn&Wkgbh1nOh&c=Czq=rqO_l)DWgP~t_k'
    'Sf*BY3vk>+-oC0H$JN)aOXHy{+(E>X;JkAT7g3?%Q6Ldd#jw&LRI$$<>Nz5Z>KW7=&r|1+7<24~fS_KFr+t|j#UzcoIzygB2N46r14^28nIU_M^ar`y8sG6q'
    'yXZ{OkSw)1nKwR3w-0Si1c+%VRf@?JtQIh!gEpPKZMtup9s<?<M4}Dp8~GbkGQgWUJ&TXYS!8#+k!&}1pIIFaAbWDu&81$luDv+&p<0$o2%ggV)JmkZSZWh1'
    't~pued6nqDyo`GNgbFN{&XFK@To-$z9CV}b#5h7pyR9Oo_IAYI)gC_gMe|*vzC%lFT_q~L!pj?T1){QV*}p{&Hbazt&cdZKZq4Rdb~m#!|0<UQkJOT(*GVL;'
    ';Kj-yEA4)=2UBV00nf21;3BIPC8=@OAg`RZdCMEHV{IwV(F9nGXC)~+9hVR7J(WyEjiKZwB8_zIoPK}$3%dWpUBa7-p8oG&&)=Fy%3b`R<GPD$D<%l!KS_e0'
    '*V6$`8wmb}{Il^=3C|#BUT1wY6fU9_-ZFgksK8NHSs{|82AvGu7^p5IyD;?9c!$HoSEqkRz|u7Oq!jkbSyMeT{-Jg$K9Kekx{=i#8@!i+Tt<{u-X)>Xcb){B'
    'jBbEoR+7j>NGY95lr;+jQ<6gCzZJ3qHQ1B2c{UPMrYoR?U@8)?W_377isf4^f@>|Rpmfu}MaznNc_B~N2(m_s+<oyv*w`sF24Z&=o`|z!tnRlIf)J8xiP3S{'
    '3M~T^_@KDQO(ib^h8n130kjKG5_iyjQj3~YXNf8pm11x~I+?Al?f{kM)l_}316g%DP{&@tL8@q$+66_0x%HRG;cLqsPIMjKk~&qWS@wIDinE=ydiIUvHI(~$'
    '$1ae&yFC`ly2FLdKI}wTrmo`E)CwKpwcICg6cR}ARtU?i=6b^j5^L2C_c}#Ov17YX>0_DqpNc{bR4#kq$Anqa7`qeC_lDlvuzS$q$co*ZKLlNzuz#CL`*w(C'
    ';eL6{p0S9(A~8S?`^)9LYE2oCEbUmtD#*C-bJKEJ8NH7-bZ1ga==d^`Yf|)X)t?VLK<wu1u0I$p$R`L^=ph;n(a(Q?YOE=TUNK<wVgP4xV!Jg#)vwM@-{ga?'
    '<gpbUrJtQ$T%2FLVZ_ES!02R8s>rK0L`Vhi$?NM{kHAvm;xy_dxkS&~M%e})Xy@F$orH8FAvJRGh21sD1vcN@Ghjh;b5e%uSd`&_dLR3!kIu9doegIJ68m`A'
    'r^BfPqua-*;<SAQ152KZ?ajOPIrU0`)OE<K(8EeBIF&Z%s?aFW;txmS&2%)5E}-taE7aCp08!5IufMh0ZLKd!$X9SO$PfYMV|_tkk#EjWt4JE(2jW&244=-p'
    'lI>EkZ+PwDP_`Wn2({2-baEYzie9tUa~Pd|;-o)M6{aJ<6L=MqMa2Ee<oeLhy^Qu=eFJfEwcqm_9jF_q^Ew0O?P~Q<+{@|M1m#+v&6m*gF}rN)#~iUs-_YIR'
    'Rb~Lx^=p2?aP-_6(~;N)s%-aEJ~I-PC2>i|%`s+9x+55Gh7;pt5mR7U-=xh3vE9I%7v}|oVxKCn(Gc{SAeMfwd{$9r0ywXv$}%*YZ6X6z8?YljZbc+wV@EI9'
    '%+x(@wHnS-GH`WIc6P&!qR<_{kOS%a)%lCRoqb<fo00Co<c$oB$IiP;tQ?Eof)&$<mEb?}pKBeJUyTFs8EX2PGuoLxHd{&C$t<d&YdArR#D2mzRsJ)9KSLQ{'
    'w1T2)0TU4nI}XE%V-dI_4XI_D7Xnc%`B8Z74s`66LeCL^IF98rIYO)$9UK2ehvr=N-LRl;t#1bb6?I3Ru(rWIc~%;sVEUj^ZIzvf^XLXR@KmzJTHJYSr`16{'
    '634G|tq5h0`&$`d;MHh=I;Z{^q@v+Nq{%H)m+er76%AXU@C7lqVL|*SlkRYO7DusV8m4`MV>+p}Bb~pxsQ~#T@1k-Cs5YBPvlX+;+_HqK#i1^$h^Mmstkh)e'
    '1Ch2=N@DIUJCTGss)wfwTPK5Z@<@AlHIde}dPCdoCh5B|p$cuqJxg+wD6v85A&C<S^GUtzGOc638^`HhM~`$*kAPM~JugUiS<*2Yjtt@w>#8+7-Hpz*-NxGc'
    'Xp^W`jsd5!GOiXSJDtWQGb+)KirJp=?TqV1_)<9{kQ;IwxC(XBExSYCq^kPh98X5eQGc9z8A)>oit&A_mzRdhc9S4+P4>E7c7UXsCDS2v>e7oTRPG*oSP@N+'
    '`NO^FWwL7cH+3XFF$p|6kBnFj!6c0)1N2IIm+sZ}o=L~Wk$^b4bidJPs25PATB1?bw|rb{s-wZR)M#%oRk$8qRVTcv6LUApGUBpHuJ&#cc;>8ctrgq&5kW*G'
    'A&1jIpe?cn-t`%p(R@+0j{eOoQ&~%OnCFoizJ5|ZfoQz8XHTau%>xiVsqs$=S8%t{NEmAnqh`cksMBsVK64+6n}2f#%vdK>wS?(38`_Pj(`sl>CTP-eX6m44'
    'zKY*CaNEWEk??HLrA@;t)YKSH;8PDzr)}cP!h#0r+K$4cmiL($`Hp31RhW!M?lfZzLA<7IPXsD#*++5f>GZ`RoNK~uqu{$rN0GH!GpR`T5X+7J_-tT<{Ej)2'
    '9(JpB6e^Yzx3K7*<=##0bb{0FN}W!WX)*ZrQ2~0FjVczz@M7-7<TaE`hLYOzF@jeR>%Z8vKbtPnP<BviAJc$hPJn`300OkDbgppl7iqP+lk8CXT>S42<-f)J'
    'xY8UZzUQEBDxO&WD6>u#4bIRZG-b~)zhO;1XyOCtOfpjyp(_*WB2w!ctla;Mo;B5I8Q_z=IUSS*g|KLc-oz3CU|Sc>sWu3c!e67_x7uncn-22dY1%sE!`5oY'
    'b=Bhl{t+j&?2m7;*9mr6VGA&dFg1oCvCy4M^+S;u2@Rop2`&g5p+6voT1csZw>e00CbA-<CL{r>J*lTc#il5@O*Lnh=*e~nC)b2m<WaNYLU||TOU#`}yjC;>'
    'rdqn2)#Tm$;VVwoHJan-N{`E@iCfOkl5kLEv!shWX_n+`oF(o<ev%Zoqd|xkw+69;JYZ=w*0{W668y9nKwsr=HJ-jIGx2Dw4X!H7C<**8Uwz+G_|*O-{wR>^'
    '-|3n+Re%5T$1kf;^-3>g9&$JUSe!c)R+kFF!Z+?*?#PCHav1p7Y*~eu>2F1=Z$IGlc>pHVEmI#*BvYgHDez8b!B6=!+YQ_POea&o%hACzpb{P0of@LUqW>Qq'
    '%Ks3n>vNmZ=2iKZdaBaJS`J!NvCR@CJ+ClbT~sVS3Lije1dpJTV_01oov%Xkr4nV}u(^mGQSau|M;6G1g{Q33G*dK%$0ESBcGBDli4uZ1UMf-B*mmf+Rxa-4'
    'wSnREjEO6+<`WPSTkj-sRG>Jdz2iL|JJ})G$@nRng#w04ZW#f$RJOFQp3~bTQ<0s%Vg7Bko4u^qq0^RX5@2oVTuu$SKZ=A-nTJ|AAL-E`^EuBZOWuC~ccba}'
    'CU<=C75`X$1(}EX@3NGKSC>huTj0vxT*%379IH={(>-=lvNW({+TqS3;D{=E62vGZzoK*_MTqVKeRJHzhFx(JB}(1iGxk|R1psw1AO!2Kp%5JC+@l07gNPK='
    'PpP)Lu_v)w)74EknaE<HG-OsoxzYXdiy@pX?Bn*Po&e>r&#s4Sz+CTG6?_!vwv7V4kwcw>1KkVz)TN)Sw~~#XvVWk1xT0;86p-@Q(_bnx;3o+XYdG>;r}6o-'
    'ukH}6Y31`oE$32iNe`|3TOn{I$DNz(OF@LCZwe5Ws(%c+QdnWmCW+%_v+T~x`*X-N*_WQRS=8m{1L4!r`i4wF_7i+?<lj~4r_c5?=Ye-t8~zojat(WTVDJL8'
    'QyI%K_=eWEPIQebJfUPx;TtOsDPf@%*tLp#?I@MPi}P2n&R)Fj*;~=xmmI%nx+8Zix$wt1)JKo6chVxRzg<O*Q8%qwL9UJ)b<j6cf!=dCY%S&1Jr}e9Wpv#d'
    'Drzjqjo}=zj-(Rub*Ol)IGH5b;YDc`6Dv~Nq?5F5)a1p2PVg0zd?pxcPb?@NXq_Wa=_b442~eWRI7#>N$eG-BP}3Oj7x6+ONM_1gh>msdSee?b$pdBnSxtZ)'
    'Z^iXyr%;Dl(&i$Nb|>6Gnl?LyS+w-ozVy4>O^M0XkA<D8bOUIEy*IB6a=e|8v+0YMxo&GjRb!%Q#htaitBtxT=9k>9je;&3-A%T==W}Fb{Pd=<Xr`^5*U`CE'
    'lv$5MV~&c|*Gp%PtON*-lR-iDgR;1fI4?@(Y>tm*>3kV!UFJ%Wk&3fdx)q}LYoSMA!2H^*lkbOo9mj4;PJKIl9YM@j|JzGqnE{SGfh~1Z47u*9QYs38xhQqN'
    'D2+>E-2okmJS@3K6o|pv+-AD3jc%g<*4fRJORJ}`&;yrzIJUp_rg?Mxxa75pew+71@A%bNpl-EI&?pOhxq}U=rEs>!SvGi$CMvzGhre9ceesZ(sXpzU<aa1O'
    'w)8AM0#uRAWTD7X?Gz3g=xaS4<S}nU^v8EiEWh)8Peo3qtQ*RSOudVpy&he-z0)5ZuWfpM`u+Lu%JCEdiH3;6l+6jUL<(7M-K044N|Ex68F))=mXme@AovP_'
    'I7A7J@>?gq@cU~w?6}K5R!Yo8;*<c})|)=Etwt#!mp*HKT~6Y*YrBbSFLifuzRXQsua(+a=xGeIZ97xzGBT)8ISYJsL+|mhf4FJO_YJq?@j}P&+}HMW#=+g5'
    '_X5|IY~lfq!8ix44!Ul`@v93H9^Kz${pE91Igu%9wpyz67)Nk>j@}Wv55+z9CDgQcvD@sueErL>Z*!p%`i1SyZJs(I6#6Mrso&2p{sv?!Z8>jVT%7*`l_)Qa'
    'YAe}E_G06T0T0^APHg3?flp}+J(b#njuEGdQ62`5aGPAG^);4rM!I0mL0yD#x5kfWl2E`18_Kw@-5$E#Be~lhR^lO188VHlpX(^?x!!(ERJu&_0aj5EnjN+%'
    'NzzRRgGNIuxvLWpf3*lKHX;1Jdqm81f?AYh(4VD#JvOeAn`RIeq|P<rzSKS?<d+y=@MRWNLikVIeur+f%GGGTys2~o)g^3%Qtup#Q~}HxNQ_XJzfjuYIs6#?'
    'i?F`oFRB`eYErpJaF=XomzGCLvq%oXsw7h#Iim^yK|E!6COLIlhbFWFGYVW>fA)DZ4~!#Bp>5}4|4a0meSc*&S(lX|v&<2m3<8uPgAS$C<roddQ-YHgim`2('
    'iQUu-WOLqcwvsB0wYC#KYwb9BN{W-+kRQboMCl!YIHTv?qduo<Sav<vb7GUdgeksXwx3rfn5jW0pO1@h4F(09|D(c+K>MTc%5u6>Wr)NUKR)E8J!M|^F`Ve}'
    'rQQ);Z7B~XN|Zb#zXK7zV5>%Ti3BZyChes21ql)H6=g6sUln8q=b7MQ<mB!2R&Dxj>^v5^`Z%S}>gq8cPJAp6Bsri{o8eWLaoNzd@+~)WX+BYda{d4L9KH!9'
    'MEIBtA5waIiDkP-W@Xb$=Gt+CA13BG6srwC#&J^cx(Tlz;@I211<ua-{g-#64)j}PV4ihQhT%Q=9vHkC=fNTW<LSb>oS1NY&esIR)V$M;R_M4T`DSO`gkOur'
    'eHO=l8ky>{)<nB9@|$#nUIMl9%-V8V0{1(r0>zG>pt<Zre{4sV=#vyUGLiOTv0fghQj22I8@8u3PM^F#UYZSRs>a1YMLKV3y0mJX6_*~Is4w`+u(0I3%^e%0'
    'TJo<~ulaK7*03W?5xE_|UUukQSG|S2$~%)rnW(~en{?}{4>t0up8i>Xc|)v~tdP<e(Q0qbV5#o(hYtziN2R^_UQ61b2e$J9SFVr<D6kB+Hjbj1lvyrk-MHSe'
    'c6kn(P{T2*`+J^pt$DmRTV0TN4cah~cDZi7xfj=3CK(wX#11O<`ot_mWC=~8ck}6Dp?+Xa!{~aR!EFm`l|(AT7okPoB#0d{)OdTu#4{vc5(zI)zX*AXO>a2M'
    'k|;qV`c)PhWd!d=1-F;=@6t=y8jZwSnxq;h96U{o1H9B;kXLXBEQc-%5(5eD#_#|KHVFfsw@(WAOON_32Eb}0G!4mQdXMBXq0!P{X^@GQRH&N)N%iAHlJiju'
    'DBLVc^pR}%*hayHPCOMK{}lRFvptO-d_U8V55~*X4>sdEPLMnR2UKgdOBzH9mu^7uf-T`4j~|rO&n&t+^30@TdR?0Sl>S@8DxOKWV}L;?&_(zJ*C@sR)T&jQ'
    'kc1|I)kxm;9w&hws~w?zxpYVB&F$T1=3G8Qo=i0vC%TxLky;a)PE>&c#@+cJF8lv{`uOmf_gAfoW43ivL@ESEB$n-$D<y<P6$@lcQ$zIgK<S|)JYUtiOc$MM'
    'om8fE+*S#2!uX#ZCr+MDs;c3#bKpAe&>1{QTYktsqGqDbA;r(3g&cE%=h?n3t9AVib;$gJj+q}V`v-LNxLU`W=o9(_O4GkB`4`G`h<51D^zChTL0!op5@}t4'
    '6_C;R?A&U^pQ!512lQmGYd)g~``wW8KypGCI?g>Z;IbGvETCWrnAUS9_0oi*Qb8yxll+z}1H95bVb9_J6ERSvpFStbyh@TM=ao(!Z!__HQUM*DdD?c~DDnVy'
    'b&(r*v=&O$C(LGbavCPQie(+y+(yY}M}u6RFl{I-tit+GD;o9Z-r)6p=FYk@OWU_kiS;@T3A89+6T2=p!|;6;G!CDnR7Kv-De?<eeYC+8Qg~XCp|$XPvMuK('
    '&iI7r?%1}l8{`>=WyZnq>}+6X6U6Uw|HGs8u`q)>a@Q88+raIMeF717+8=u7!WifRMl2b+=O%dco{UCZr9u#{<n2WcbDB?jsND7#QWD$i^@slrdl%>uvRchX'
    'T%Zt;(JCiTyP5ahBX_7`iZ0p^T+GV!SEyKcf9wyqc$?82cs>mN*Y)=S2XyW6?oM4`9ylDHD@EoaxTq2Zksv>n5XY0+UmzCedb;=}dfIPN{MUVBD>|V7b;~WW'
    'mc$k_QugqOkTuXaUBq;%&Ez?~ld@LSa(W>u#Z!V+q)yR}M~gKlNi`pZdbttJ4}|^s{|jVEm1CSI94YiX7r7&)olts%U68brw#F`Kwn(>doVE_0idAs*W%22c'
    'iQ!)p!B2zob1(;oMFG-_^s@IGjw|P7ik7vczylTEb(NfaDpf^y{Rf<VjKV^gH|RQLd6&%9l<@h8lD}hK3pTUgtriH0f7jQUqql7zN?xp1(mc?(E3=&amjk<k'
    '5E;al86AZTIW7s1n0f3){^LCIYXA%)9Jmo|czRE%f1#*=za%DV*Y>fnJJE4qyAg#Fzn8wNo7yss8W`AY_`mpzqF@3l^FPeqENlSTZ1|1S%aBt~c!bIZS7b?4'
    '+m(zEa06?bB2gHOlslr7EWP(>L;e~}LBMGo!L1|-V9R8f%|i!{l(*nwO)lnw1-5cAx4iW1`A8ZGvN8E0e&y^BgQc<$$;sgen(gQpg(-uoCc%|KjTWOo&PIdV'
    ')l6%z_y}Uj!D>#&llM-AS|HqG^aXjYN1UiuuT~EjZ@NT+Nvox>BK^GP#XOP+woouzog65CVGe6Y^Vjh^VzNg2D;5XbJOhomixY0Emim>8+z2Zmw?gV-t#ps%'
    'vf!oh_tbz~pG>y<mPXn!*hg07rPj7wInVB9HB*of-5IsQo1M;9Ga0r!l)9dl*j$o}M2=}<4ryYJXm7rE(EINx482FCZB2mEcr$FN*^|@**Bz3+?G(c#STG17'
    '5>*>@NU|ZfH7(@0m_LhHJEW9JU^W{=W=;CEm<7_V$o7XaWi=Y<npPFn?2%Rtzt*#>BZ-dIf6eMP?{guVDhW}Uw0NXBG3}<u-k*iXC~-#F?IO?(qu3Z%QJTH('
    'k<Y$;sc+Vo#^y*Qj_-w&569UkBqtY*V+H&8O$3rReD?8Zy`@&Vr@$snk>~`J5Bj;KRM5|IJ62;Lx}v`?gX#)=5mLVhi35Qy+A5}!w(|-lU6=RMJwo}%d^Q}w'
    'E@$aT{dlC4$a_v(Yn}1FR_^#eKV5uCj~jGtk8S_Lg8gX_U%d&;x%P$da7sNI3y7cP&*=Aw?n|ds&YO|C@EC8#yj!8y>SLS>g>z-3WljtT{DooUnBkWx(#}Qw'
    ')pB|V%QHZe1==~4m*MX)(?6a68UST>URr*ImM$Nild|4Du#(V+g&hX}SOc{nx%{=Y^G(`nZzzlZg-ov?9<0X9|4On^jc@*3CPT!_=`b62aN>Zm!bw|T))fRu'
    '-!727wTeI(&-iIV9qtqrFqUHGg4eIlE_$!uTvl)fCz;CWQ7!R<Ok68P{MaaWbiyi(aPKN~MGBCxy(5Y7RITJ$bc=%|$rr~4vKCi#i5Q;Ulz&jO_`o_&R~!zO'
    'e!3N6M*cEVUKGouraUoGU|BX)Sx9c7s$5Kn=a;5~Avz@ih9Ti2JTeVUs<VWlMLVFTc2^m1qzAeTd%Os+*7l~5(31fWT~r_exhCqYeP5TU8!N)Ga9>5RqQP-G'
    'HEf9S)KrWkJfP~PylzDT)dUtrqB!UiE9_j$IPV1$cS09dcp;3>6zYt1Ep?a+!}L>I$LZsv*ab$z56n=c<i|Oxoe0f9+rp!pz75)np4-!_@#r11AV<*@Xvthr'
    '9hKB^TdTr`L-Hp<FHYEo(;?<jB{`dtI;zZQR}YGG<K)#PU%~9=VL_n!ELZ2FYb4iPb!PNI!fn5ym^MSZlq-%Mh7-F^W%aUbKQk2KtzGnf`9Q`JUJA2I^5Lv1'
    'iR|(r;3biLqzsAgQWRIKKy^KkkhN+6j{QmUNrP3*wvT5=J%o*G$?n!u*sjpgkcxmYOOBh3jwoM3u{`i?H}-6v`9brX)l(>aMCVOHeeiei%0<UAxn3o7M@Q{A'
    'y>*U;r7zddPwbeJQuB7+h>n67DVyvNlz<O%t(ojM4}GrjdWE@|HuOFA)PG&a{n)vcF1g;)E6*<CU3p<gr8R01gS|r2VQYa36*xgaY!59bsCkmc%(<{f<M14w'
    'eMF<P+A1a=c4`B9Y;~O|9qX*#Gr>uebL-N+s%PJ5)Sssif2kFF8?My!2smQ+nvOf=Ltt7gz%EQBh1Fd|?9UIJ9}t9hMCX<A^m?Qfnq{QTOk3hzjpmI88m&v^'
    'obwzmuR71(Nvc})GbVj8Db&a@0cr?iV*m6IS;W)e(zt-f!`Gpwnkt5gsG3NRj`~FN$wYGPhsGqZn!rL$#~(PNTQr{32cvvsHsTvW<?5`hT~t^q-KvFf`h^fR'
    'IubA-%&pZxtczUKA{*!Y42)3;@dYDI8%c0!oadpLcRzHKtNmY~H&LrnASHXD*G0jZ>o>cj$jGgY1VMSFEeWi2Ngch6zqJZ=GsUr#fu`0gKFFIIsQG+3osNMJ'
    '-cdrTSvJ30akwNf(+ku_w0rhLQed=uuTH-^zi{&0jQdy9xvga62MiZZDM4xP@zceue{bm!`JtWFhM$1Q*4lG^?K{5?oK(TkEq;ZJ(7VZ<9Cf8OGt$RbkD?Sa'
    'x)Kapdr50QX|Xk3v@a)=l%<;U0&w|3ETe<3KQ<3SVb_0&zULhGl0-G?OP+U<E$SdcWsayNOA_6WmN%I2{tiwtJYG$V=S;NB`ge{?K$^Dp4Wyi|EZ-Z(1)u~G'
    'R-23$ti|jRYnGoDXlentj`GoQU!<MUadO<joW8=%t`Z8d3Wis4ZI`2bfR%nz6k=rxxItFy!y@rS8Ms?3>BXjrAc_=k*7O^p#IC=_smL5JNFdCUVu<XrkS<w@'
    'd<>SEStp!}+wz3t(Mf9eu*0*XzLQTRfgK1$Gn`qP$fUYQ|J|qm9^lj_RahGQb%+7n@NAEs?b5G3`tLqIi$iBXhKUe70RSGvHcNDgy@C=-C3!QYxS>lF8qt*p'
    '`Px>y?xe;ceVrzM6!q*=@G6hkMQ}lqoeOE9&>3_*!+QQTnpJrk6Vrgt(>j3W^gY3#Lly9^jyB;JP4glbbfW5ExJ>+}j}=|%D*E{O6@JJ=POelRDR_b^Zg#qH'
    'VZF3BG4cgV)|*`$dRILn{9W5)ocCnxrxAq7Q(H?nPz{sBn4&-^0tAiZaQ9f(lDmhIGEm*|ajF-*BfCKR2%1s}PL=#=t&o?8h(FKMafAsrU(xhPSvT;G^`+4N'
    'MQVyCLVaX^nC+?m(*F5GE3CUXwZ_k=D4M(Qv+g~PeRn<d?Qe{uei%x`gAp+hB0l5O$vv^aM2z_0j%TgtV14o8{O9jpzCQatz&N^<=9$KlT5`P(V|D~;APYu-'
    '|MbgkYIZwpccNj&A^9lY4kEmhBHBjcS|vJSRPig*8|oXfNzNy0Tk(PGqA)kiL-EzQmxB2I|1=K9%U7y-l7g6V=j|G{CKx}yS<a0=grVsbFf_DJYRx~KrLlr)'
    'HsEdKeEI@Qt(9;&oo=<{+{p=fqKDX~8C(pjV&)o+#0lvOd*tTtoPsK&g!r+|ZmI}%sn8Xq(d5=SuksJFdD%+#&3sw|oNpNY$7h5VE1>er^wY<O&Qgc=GW41Z'
    '!`8#<DAqJJGxV9RFu04@c4lUdp+r<YetKaHITlC2e8@X@OOr#4&e8lxPCNPjxUIC9MMtUDs*O%0+i3tCTkoHm@=O!ow3EZ#P9XMxk-WcF<hrz3e_yx#8*R2N'
    't-h~S>7|})6$PuHzguz5<VhobEuRG~u8q9PdAm`5mS;ub_+;EF84SbI8s9<wJ<)go^gX#%a=5(gr~EonXO1x#8OL1PZRAnU&55bee=ylrXo2XkDH8RGgHk%Q'
    '=S;9t=Y66AsyYM=^f^{%vzETM4kyCnEtd8Ht)=u&-Y!)z){Z|r=_C+TpF99>%g&F`(~dcTNE|81##ioBFn?OLdRDi5ZLP<N{k(3xQ<FN9yV$ut9JZa|0@l0p'
    'YSgt2%927|8nSPv51kJNg;_3<^|ftsoAfUB8!lcN{0?|D!Ba^TNbrd7mk;)xBktVE^!gfzlTprLIDxoltdA+MeKt^U{5Zc2{31RMK^jbFVuhCNol@D$PP==g'
    '9~mo+dgMoh%(O2E4U2bcT7;RYYw^?m&DI4u<Xm1&W4UH($jhjvgkeLQT7Zx{PWa-hsGRV5)oM)!5tSdu>L^fNSE8xP`N?=zS+%YAx?k&KB@7&zlO7)dpz(E|'
    '<iPK2geJ~n&FW2k!%$bsO2HMKl&^;4iK$N<#t70G69>{@%Eg?!WwViQz1i5Pg?Fp|Ja2c~<QukEnK)W$xZZ3yL`pq(2nqXL(xLC@pojv9g0O;LIf852^@OAk'
    '1^FJVN&|l7iH@2eSJwFyO{pD%r1>12JSDLgO?%o%%4av{%<UAnj5Y4ou?#WJ3&+E}q+)H@Dc_OW?wI%eHq>01FD$?Y9dGHy=V>CHOvl4iK6J{g`eQr3s4RuN'
    'lh4OHv300F-slk8py>|1<<4wWi5nU&jvwmCIQ8UWb1q#>GD!_$ohDMU6oQ2mpDZ*H`3K859UE;2?s0+NEsB24hf{`gU7-3BtK;%WSr<K{JgkJWSs)XH2qEkS'
    '%2`04y68?{pkj?hD2YAjFb88!^h?4egin2?bhZF#0ygY47t=oPX|@_}19Fd;BE~1B@k5n|H3599?dJJ^Q?Ib)v9|1)SFA(p>BwFw1haE2{R{YYZMtWrhC0-i'
    'hmFtQ?8v0)uyb<k!oQDGUlO&WzB##f&RtmD=aME*-RcDyz?_goUo_1zd#V<jyHM>EIH?s+m>sNU?!CZX(udn54|HiCb`2&vjtz_MYSJICOXthY7z@z5MJ_z|'
    'O4g|Lg?<-B<F_0x%=O1RGf>R(w9tBXJ<i8F=jgj$J7KxRu?*1v&lqEXB`~G{J?;X)?wli3UV*P`-&BFPf7qk2m#Ia8G4sRnhM-0Q@hT`B6lG_#kKJ+F)*k4H'
    '#<HQtvFJWJx|&W_3p>veqaExfd&z!skb|K1Y_A>>*bM*V@wg{CDSH@wguz$>$j?WFc#>`ahT>I-lft%DDt0_1vUqTu4r|RiHFumg8H;mhrUY+N#8hc}Mn$Sl'
    'EgGqO<h9afrNwG43lg&!xKgGk(cfLFN8K8a1=gyrP%0k_g=y95B40KP^5s`IKQNO{{z~Zv3P#5~(RNQZ%>Y9ko}{g3Ac0z_gEgxmpeGpcv7vRY)!gfZVDv%A'
    'k22V()4S0i!aRXqY)2ja5YdMa2_pIc|0R0CKQI)7Q*m^nH_HsYj9+D0^b@M0qODic`7ru<dN++OXk3e}Bzgm1Wp`KEyxEEtll~0Y3J$P4*zI9L&nOilAx|#e'
    'x=)xe!ZRIw2M?JGg@>%Nf+tM;<cXqj@Ek`+v@CjZ@Et|lHFUI{;}O;@z`-ftxi^Q-V@UE6ARV;_AAzQWb;d>1SR?-#YpH7}O`e6UqF*=4PH=S#t{D|hpIQXU'
    'vdVH#ielUhR!q*o%4NQBGR)ek_q6#hK-}p*>EVBS{iT~6A!jwsNB?Ya!KgH`CT8i!^Yb@nl+f>YovS;T2=Lm$*fObOCBw3Hi9sK;!HTvSIu#B{ME)jiglm1A'
    ';BBHRj>8plzCs>Vr*ih=k21DS<>!~L{-%d0i3~qq@+~U!VjH`eQGjEAz{yYPH|fM>b{)K0g!v@0TfGLMiXsR#&}>}Wjh{8QTe~Nz^HRqWgeL}<2%6vPk-k%t'
    'p4>hNeC=n{Qm01mdBaIDJE>_N=21tz`t4}ufgG~85PkmSytYqHs}*qFCxR?-9!!%rz%~6E#FPT2QZIb!h*S%loCO<GK6?GZO(w{gi);z~?!yqO6`{h?eb#cA'
    'hzG1iolvTwV@KnB*B{*8_u+1wXN)m4z<6w_DY`~<^*T#nbsNcu{C$xPArS6uCu<NzoWa~b+iw-eo$WUdfOACV(FZGdRJMy;oEd8xo`BNxluQ^;Q|Rliiv4;W'
    'Ow}d`RckSj;#{6HTqc;llxM8Q9njBf=s+nQv@MOefi8LORa}&cLLVY}he_p59!m@=hj+sh5$b#y%2oVv{Tu1{!dDwsWUjV#N<b`=*LM}jRgYG@aUoK^#hWPK'
    'Bxvp{=p3E(Q%Yc^R+DDpJVviQ`vz=}f(+a|!gfASN2zKxs!c_NR#pnuW9VBR>GspJXM%T@+Z4&OXI1;1*X8(gv1S-+_ZB@jUwC$XWYsvISE9L-*oWwn^Zy(s'
    '9EcltYr5jtlNQvx*)qdM_f(<iuvd!H!4xMgkTi8gNQwA)e3F{Pig}2|Z^TM%NSk~X1_Ij@?~lvhz(r*(#9Djk0*yH3gjepnLSh?0wX?<V6uVT%cIr9q!dCH7'
    'q$ZSq3OK^Lbd}EFsg<tw19rGHNh@jDTaOA#XuB#^_o!&dXoGM_Eml8L&-#TBVR=)l7Ulm4lrUZSCiq}_8I*R`Fx6=z@z&0HqO7z^q2gtHT!WBR9<}LY;lhI+'
    '4&D6b&kNmj_Mp{ut<N#xotE|`9MkE3dhyo#)F#Dc>U$R>DNS4LuM}chAZ`^bG#LfVHX^cERMasH<hGtM4CsUUbi;tIePf;Ben-J5vx7dyMdFl!1dMwU&0NT{'
    'DEO@5Xfc3(AehVifwhSPhC+qL_h?V_UYx%8>C9Ko`C_ub-#+1*<!HwP+vuPWuy6%1Io3S_S&qlkdky>bu79U<2}*9!uco}4-c4bl?+L!VdBox;3s>^y1cNg}'
    'pdPkVstTJs%raVgliLY6qNkVSkl#IG2tR~>UmJvotFf??Gb#@7hEZ-+=K7rtMM@<>%1|)x5Z2W7J$bbj@d*-Q-eGhjjbKUGg`aAXzbQ#)gee<*HP6v>rnDrv'
    'G&kC-uq^SPAKNjV*|DjjD60Ay{)#gHNytVh|IyfJL5pBr7(0BrFfnum9j3h|ovVGBsonCL1W}E2v(yc{iIc_#{iqj#=L_6DFz3w<?R@g@z^sI2J^B9P{Fh2#'
    'LhL5(K!wtIes%id><gz^X4x6>BPTx2pCRLeyDlN5+RXF;aqr|{TbdkllYkr(Q9~hz)mdr$O)%uiix*}}s2(;P-z|rnUP4d0sYy6To5Q_yIaEmQtN=x(Djs2~'
    'JM5sc7HUJCLnc<XMKqm^A8@rN4AFxfLAaS=HW)3COC0nu&hA=ZFYox;J?Q=N)9ITt+md$B`|14R<v-3}yARpzxcB|(-^rY&)bJ5p3a~Abh&Az1^&p8__)~Q8'
    'QFSkg+MN4ZU+4vD_sGhODQH8mFOdfuLz8|l!s>nc4#AU^;X>uwU@Lm;-n&pOGA*^Jsmw}<LYFPzxh`^&N~N5iRz0rs(>VI8)yY%=5{Whg>f!U{*-_**V&i5!'
    '4V5Hv+=H#PQ4U<HbNT#C&`bmQn3pQ^1Mn{W$t^Hgu<n!Tq%P=sxDAFB9j{c_uz%91iQm3J(+;t_A2PkcP@;e%vKU>Bv*-mdm{BHpQP`me)ISrGoDH|#p34?;'
    'l-qB~s<hx%VTS?*g&v;%@b>IN&o*UxRDI>t7CiZ?7j}iS{sS-#RF#IsaK@QnHk`o?=fs!}2EdruJRMBlwv8$WJSOn{k*v1|3nwp+&Cclf083H?Hec1=C+bBU'
    'J%4WYN(~j>&-CwbYbR0bFqamO*39*uR{NkvulcMI;ee9s=t*m@gVi9Qm&QwEd@nK*+)wc)0tyDwHLRb>v^^i)Ay600{nhG$sL5f-2!H6A+~vueGfaH!ar%dj'
    'UgnABp3QU59R<xj{C(Kw<8#*5P^@JV2-rQ`qra#ry;=e7#r^kyat6b#Ee0T2uf}i+SnW?o9d!lU>ktARJ>||}{FUuCUuK9YO7>j@1X#e((kwm!9dPpm)h?WC'
    's|*xw<4)R%ESO)gHVJbJ{E-6}oG+ySfG!ls9wz=Fp_$z@G+AE25(2XV6mD^oWwVI$_#jlnwx9>8s^%GR2&gYYs!A}3o=gr0IYH+0-RNpGM*mV=Q4L%Nq~+ao'
    '+ja3<PVXmZ<ycJ^#}}P}(Yh>*Smp1h7q5G7-kt+*7rQAw)y(Y?O2#Kj6kV{{)h5>orBBjk>$8VdA#>`G5};a>(c)%PNbQ^>kJ2BYgIqAt5ToG+bn<c*oEk02'
    '%GM^3l`N6Ujyh@hc!qHp&0D9m>5nlX&0WU02~5$K^FH1a&-?SM5&R7|`~rQEC&==wCgK9%0eOed!$!UNzXh}VD<WS%9kW_(HW#?sv!r<F)xP75J`-&A&)ukE'
    'q9A2IA`4AFxEA73GIb|FEp7n*nj^+(dwf&0hXaa`fO9>Q%p+z(&_yjDtSE!1<8;{66@S-K^`+BG_3&6#l{Y{0Y*_hwi;X)ugS}(vK@hK2SN8+Y;XktZ6qto<'
    'wvfx7IaHQ?7h?@^ZDAhZYFH6+?x;fD%^f(4-2#3_(LcNkddRQk0{GUI*XAYZ-PeZOJly?5KsJ4w&7rS2FPfSZcUpKBa<4YT)BL~0GNTP4{>AwO6G-8nvg{v+'
    'uKgoe&M|%*78^efzufq7_*mmdyGdC@mZ(l)H->1nKrZQ;0qIqWIKdu92Q8FUR})6k!V>+(4T!Kq65I%(Q_0ds4nrW<)f~YDNO0QE<rjfRRt!G<es%iBjmSUL'
    '4)J7%ui~ajT*7Vz;N#o)2slB^uYJTgvvx8I(x@d`=eNmKu|DE{VujjIteas{99-{(Y%$_=QV?d3powMi@%8sS(n}g$*Ut9)v}k;{KZT+8<-MxCr*-f;rQ<sh'
    'wFloP)OBaQhtO-hbgF{wBizPh^zJ4Ex<G%%M`MIZQEQD%D;D=WzDnW8I|XPSJ|1~Mn0jv`E5O7o`?nc00-M1VYz~EhHHQ;UpWv&`SZ5SS$6i*3+WWfs+F1uI'
    '>8!xjYABGe-cef*sKi)C9DY(1B%;$}U`8Gg{g&B;K+*|2O+)b@#4qgK8C*X=ipV!KdV7<h=1nElfR7rgGLYpMb0vC*IBev?1r>8i5FH1WiZEKuuyV@3fifj*'
    'M27THx<&EO|1|65Lvm(iSU9t8y#<}JK-R+9H$DeYKzOS29%J-8NPkjgg2>Yuwn#8~jS1VKb%=R+93TW^_CdM;Qo#4>;~hQ6`IHzS3;KL1y18?&n%yJ&T=2tI'
    'H-P)2+f~#_ntuPx_Erxh7S|sNA=BS!4S&1Q5I6fB{7dxuyN$-@^_9LsQ=C<$pl>xT_^lTFtwQ2<vHrIgr@w!9c5(4{EC&yMK6`cky3#pt+fzvmq3Yw*0XPza'
    'zPf-ZLJ4l_0UBl~XAIoHaA%>IYn|7{3PrVzlW&zr%ZDR_c6L~!aJ+Z88)Du!cN<un41^UYWf?)ZL@qYx%hG|U6N&B<=#sjogRQk4Y;`R#8qu}{5_mY;mf1W*'
    '9xQD*K9N=pAR;sy+Nz>;97Jgf<k%#aBf{uE?3%5kOyV9)sG5xOIdw}Fx-E#dP%NK=Md$J8H;YnTtjlh3b5$Bj+))!NPt~T0YfdpYvn+q&Om<=0d5E6)%am?b'
    'P7VRC<G7o$>sf@2eJ#N-VUQ18fSseSrt*^09oBXI!FZy7s8TDGh)ww%v0dB)SxuhZ^=FK(nYf9DK{7yoG_~CK9s??>`PrP;lSs6fRmJ6Xi`k0xjtn`+f-iDj'
    'uyVvbDwqc9=1oIr*{UHOhQ*12Y$uZPludRwunYJ{B4^w^`1mG#csa(HMbSk6Bsr#+=7m*H;i*omR~zN<G_?UYzDQj`$ZOb@h>T6csnFA|o}@*iD)kBn-UFr>'
    'Lr*-V;gL$+Xho?aKO%1S)d8%<XlTU~XxYXR`!<*|Q;)U1X~F{YR6IS@djC4Z6xUVk082(RG4Dlt{GLyXwWu1ZlJ#Hk>HFi<Stwh;@<c{@oyWSA72q+@EF{=5'
    'CC2<T9pjB-3|DOXAV!cZ``fOOL>==XGRo9VQrK##NIDAwkmz<`Tt~3WIZz-%k6oH4`s*6*@#wDq5M5zN)RJ8`hTES0#F)641oIAwDFn}p!W+?sp!cE(P#Sm7'
    'K$(|r{0UM49Hzk|!tUw6%d7-V_0ZnWM<lB+edtgQ<-j(1VM$%o2z(FaLJ}E#?T@$BJ<2~)h>94|q55LALU=AouVCEy-as*mk-^Wrv4eaOn2}DPOVAhPg@iNT'
    '`%1Hp{IZ&Do55UgU;))q9fb`zx=|u;MG4O&cr|s<Lug!*O>N{uBm4VS_XfAGyJ@?nX3kKyH8~>|Mo;1Tvr)`{iCI%+#sY%3?l)$mR6k6xPN<uSsxFtFGQ=#R'
    'd1nJwv2>F-*Qwf`p-pm3w^BLx8U~0AbxH@PyG*j~)>mSaX@d~ou%<#OB?-~;;FHB)XxkNUl+e`GOYi&G$*O(aIyhL<*Q`Isx!$;^T>fkIGt>fuMCN-GEQ_~f'
    'Piz{DV)*#J6ju+IrWtB^sGr(w4#^4=k9v7cCiCN(dcL}0bN^|E&9$L%N2Q^4F55ugSk7u}8#1wR`jL`9^M=!X&*&D~S1H`W!7XH7=*2gWoWtTj_R4xhApgQE'
    '@6ccKH~>nTgz1*mpS+bfH*Fil=l!Q-RZLh>@Dp&kFQ$v-&#+tJxsz<sQHE}uV=+M8EMxD!W9)ScxK`f%Vk__dms@%FH@5Pkowxq={)g3lIE-GL|9bKA>;g04'
    'ki3PL;N56-$G&ySwf1f_WPyU*K{F6hM&z?k?p)}Ei$Ggg<HdCK?gr$NoyK1gsSArBbW>#k2YlYYzse9RfJK_S(fF3M-yjlUg_B4H<42@m!RjP<fSN$(=*1EJ'
    '$|gYX;UQ4v1%(cvU^C?o!S;)u5!3vP9<U&qU~P-3@^T$rjZqAv9>Q6eO~<3b0}V{-!!MD~jP9m$LhFxEgO9$2&}#o4Yr7%#484z+_Zf7PqRd*X#?_yr&o>NS'
    'I)ObvG4Ml%b+Y`2c|@=}>MJ(}ACTcH>hrjP0F7W}mNytL5uqSFhMAd0_kHr4L=QzYp{<tFI!=jNiyzQ}Prdr>uqW%>`{CmJ=iX27BSCBySQ?piLW_97Ua1Z6'
    'ZaN(<upQI{{6%I?r!P<%(TMDS?D38&J|Za*y5>Yx{4X0guIE|SQR|Df!I|JROG~qAeV(ou#x=f$b(qRDLIvzfI;@LINMbW^`DtO*l*=B5y4YxlO;6FuIipBA'
    'EW*C~61p!=Pha_5S+o7}?b*-hQeNFMMx?DI+Cp?F{1;)N=r>xFwqoa7y;2wt(fWV?pPu#Z^u>#_H&ihOy8zuqOiBJ1e(%a}(lpwiz5M<a2G*F^pif)4X4r$*'
    'K!bk5Ki-`G%72`}eL{Ua<9{)9Z0oaIqw=7)+R(1`WXB)C_Jh5PUP}~>9;pZFe$)@FYfYQMJ{<PcYupp4FZ4rgKPJ%wGzM>kd4UH@e8R;XLR`JP<WY6I(K8hW'
    'v-}v<qmOY^i{LGd)qaaFmmfXrCKcs*a%y^j!Vgjt&!_zw-*Rq-(D*QHxr*m8p}m`sqEwq565@{%B!Oz+TU%Sd!<^LNHJy3^aw63{T=2tjW*=|zo2Dxth1n$#'
    'uLZpU>GOKYXLuWG)bfRPGsVtyZP;RYggLzwALs3`PEIdouzLgU)EIX{BclKm8&#cFafTp7<YyfnldMcofNoX?{2!nARK*8uvHpIGZ4123VKr(IrM8kXbkA%l'
    '^Ft2N3~J-_E<6d)2XbcMZg7GWL4KC{L)d%{<nu<87MwWV&KSKlnpE?oAc-s$e!ml`q?NGeIItGCrAl2X51ZO-kB1B6*~-qFbCT!-+UG<Sx*F*UU&I)agzH(S'
    'UCUF%BMIz$AFal=a!08K?AyZMTWXO+kg#6!ldY~RB4eoBepBOKMt_Z3JFtEsDx2T6wsrvTxRmR7{yehm=;DsE1qEOueM8ZEj&l5xUUfOH&wW8@aOjoV$dYdm'
    'mLg<w4`zxW+XjC&RS65ZOGFU1H2Px5^j$t^q91AS!%MM_OCvhg5e^-EK`TO*#I3IDC!j4pcv3BMn>wxtnpRV9a%m0a!0N=;#y+ST6*B=eyJfxI^1KSLai#;t'
    '78xWM+#Ak@XPK;>?_46{w^U2<lqmA^EULPp`*23AsAi2;lo9d4P4^6UY%NljMcOj76ZQ5{R)KSjwzWw9q7w;pM_ofkF=x#_C!}0Nwu>@dTAcb|p53c(O!$++'
    'F>8@RX%&hb8oN*3RsRzrTAFqnVy}j4_%?GCB=iHGc#x_3di2!F8eO1+y>^jOl`|Jn481LablrL%xMf%>f?nQsi1vJlMMRE1h({qeWarnT^sPCjP{q<f4JVPE'
    '@sE(oQb~4(vy7d~=~1){ABM2wetHB!Vlsi5Q;9FA>VWTK7%hT1jP!|oOCU4E%HShy+zESnWC3A0gbsDMQs7o8`zrj#_I<>p9JhM8<?yLMlHu4kJ-dUV|8;8n'
    'Qd;N+%mi@hs0>t^K>D*>2%{=v(;tcnA;?;!KwRVo&Tj)eApvHC`GvrA7tQEpw|qK_mr9#XqX~nHVzged!>y(Q>{W*ZP(3jg*{Fe>%p`z5t9mXE?Cf`nk{BRb'
    '4`R0T8k8Uxk!YOg8!@2k+bhve<fbzHA+*^j4>wCrO)^ZYA0nZui)tDNq20H*n4-YeE@3B2buCJ<E?tlVb0G#+X)&F{MNu_VFAL^yn71D~QC*_H24Yve{XipZ'
    '#27>lKbqYDyr%b!T2f#cqt?bGK%3Fih;4z>5GbDk7Q}P1g$Bkgdc?tEcuLz+q)A1vGcZig_@^QGq)pof7{E!9VwbJ1aHrN2Z|Ay8z0Cnlx_n$%aD+b3OB5*!'
    '%4)Ns;3vZ58r;Rs2K8R@Y$a-6_~@`@6qMv5rl1o)n8$2Hf}y}a3pAy!PQj1ie-ebCV1s&sg*I3i2_nhAbA*ot9!slx1qs}I<Uf>(kZt3-92vo_PjSpdg{d?g'
    'w&v#?VjO{cbk?nmQd>Vs6Qd**?z7y0%Eyf?2~N*L7N%&uiAh%96ADcYmT<T})~jS|^1yPpyGQZ^ih6I9j>bNRXR$?(xBf_-Jvpi~)E%*U^XU?~VOX605S7{l'
    '6=am>Tq3%fPHz#RWFaJ9>51P8>mOmr8`QXv@23-^;wNW=Xz(x?qgGlfBmm?HWPTJNhW*j_Az{ThVuLSHpNsL_tvc!@7owiO@6VhVRF+lHJ|M^wc=%u`wxj5j'
    'EC5(}Ccs%T;s-<>Uqn0Xz@>WAPH0@;HXEo%$2jtA=(LN~5hM}K0VV~pXNNWJFuwkLLEJh`a_{2w?aTA%BbDSna6w)S26LHZxC+-|*I-^i>HP8E+f0lF(bWT*'
    '4_JYYHQvA<87&N{p?{|aP?tW2eqZ|oKv%mNuFhzj8MXP%6enX$dU4=7upZNWvL-7S2Ohv5qwuz8D~(#)4g2vAFE8G_MTjJnC7m~Dw3HVp;udv0jdq;RzB@nv'
    'SvR(`y-NZxMJ$p%hiDC}`w^Z(xz@p(E3{87?X&W3KE0ph>(&ipe|y#lUG+BYogOX@lTi6h0Ic4_A_X_SeUcU|td!b}^Akl$PH*yOD@wkE&kd>wES(%BGuetA'
    '$R}Kt8O6FX)f|p8ZG=J@2e$-Lt(_#gS}m<(PZSc}C_VDF<5aI+k`Yk|D3q$VnULYR|1esN^bWKxu8{65uims6_Z~`kFmXLsgQk_-Jx6EeVPf`1NmL3gfwjjW'
    '7Jh(Q&daUePv4$hY;`wg+IzT<S+9pxU-m}bJeQ5U2Co_`n0hm%Qw6cRy?I;2QStDly35`S*nIk@(aon!vmpO_%OqmNf28I;*-Mx#4YnUj5=;rUv<62Nv67<!'
    '>s&vKskrn#SDG#{;g(qhI*A&=5z4B-gyCv${d9_mJa4xGu$&=DH^&{?bPRYSCQd*i2dj())?6u>0k@<`;=)JK8R;SRg-|Qy^1X$3l&t0!5p@}DEkZ{rN*9@b'
    'sa-pDHI6n{N#8`~Q(vf53&d4DXH@+pS4y>ac&PP|a1rAX<a$9q3|%-5o=KE1BNqpy=z-cugII8_X@W&1af5`e%wyg|$97Zt+SHh$Jom>%O*usBh0s1!15?^W'
    ';FW+GBd-D^by<IK)1mlTeT8ZkWHOD$Q`ls4x;PgWWC-vktC=$)?j2sYI%*|8A~z>AN>j3;b<__oG>oZ)KcT+nt{uhtp3J_eX{Mg=f=l(!H`)cTCwF7du^elK'
    'gQ*n<A(1)|xks8g%dw9P>C{xWIDr6ext33HML1W!z~M?0?59sp3-n&qFWqF&ODD67w%0<jz|o;oV~@&Wk`_5?fe#hAaL#d^=tVOhlBc5wdD1a3jAll@wrAx('
    '=Z+2CtAR17EkibBd)f-_3esfhp$7`sb<`axIKOL1@Mm_3?uEzRDZ~Khq-`5Le<U^+;x!8J?0}iGa#_iBP8N(ykDJKZSiOUmpYpsW&^fypD{ieqpo7!36aMvP'
    'Q_B=QrP{gp%azngNIh4mwoV+)oyBge(J|vh<OGBg=jM6iao;!n514yQgZ7h0oUqNraEt#Tp$Xqll&p@ZpW9vp8rn_VY%r2<A#&5f<VcHEPc|O2T3N9sG{NNr'
    'JGXO0bsC~SG+Ef!6W!L@d!>}Q!3!gNUj&r7=2PxOU3FrUi^I{-61kE>#NgPvGqZ&?mZ~E`|EDT*sdrybmrK=su`1VL!<8oYX-bEUb-DI3eTgbpD>lABlN%(3'
    'U#!QqYyJ1Baeq3y_`U-i(`b>|?iWDZ>di*<F3a#>Ed)aqxgN{_VmzYf{d>}6DmCsYAuSKlZx=osqmHu`W$)fC#EqC-r2EmgyA4t}9<k;Wi7quj?0mEX0>N}_'
    '{C(Suu&lmqHTYw69)|9~Yx3gevMsl4bFX1En_9<=R}S3ZMA3PO*+*Eh@dNNvw;2p*K`5|{p}vTKfgg>B384{3z|>=1gr1&=dK8C%8*@BH+%uDTCsC>x);-hR'
    'q_nP!SvDXq^rdpVX0KqLIfYeJuBP6OqTgYrL<ioF9{O`qy#i@PDC#MxWoeW|yp6{@e=r;U>tB74P4U%Wp7rnG@5SA8y1W^YvVFEVqD6T3j(<^SsH-$-(E3}E'
    '$nZM7$>u}o8%O^N;yAf@nyZ!i=H0I1kN$v}I^QWAXlo}LXK(v{hP7L;H$4V5<4Qt7%viV3I_W<|#f-<L_w&owJ#?Bz#Vl-O!&%_A71cb>Fp8|a>hv$}aJLfl'
    'z|K`d3sh7I9zUxNxTVj2{IU1ur}JOlFk-#YG17s;?>eX@WH>C;O9Kz}5Pf(0x3i1Cg8=c}#jmel{M38%%lX@adV4R<e^*HQc-#uA%#TcWtF8Lvd_E>{X49o#'
    'UjE}Br?3NGzBuc>xHvog8UB9r^ZEJPpI)Bv-A%QN*h!ZefiA&qrd`;ftN4>V+drF+EDv$2!_}YT#_h>*Ot+vKdN9xK=c6UXJn;k0B2RJL`cYV$PVWXcc#s{y'
    'b~-~M_+b<WD#Trc=&kN!)aP(8d#X~xfFo`97OyQ%hqbs{%t2BS`o?e;RZ|a(-hsV^lw-@FR&VKQ^3r!sxxs5AoT7h*;{3fW%POjQI1Qme(r%&7;Xw7C(NEOQ'
    ';Rjzdcsc-zbV^xoBxbv>pAQMU2+Rk*3C#!YYKH;N`!VB|dy@G^LP66KLq}f5;<Ezp6-TOcPudX~3Jg&S>*Tpi6c?I%8u!)GI)%hv#$Uq~CET^G0K&GPz3@^u'
    '9~N<m|CAwg#gouKvUx7pA{-#IS|mf*Si4T>p$cPA*L<3vJvWq{pO!m;sarLTd~$dx-~T6>&Uk$+EOAF;=I)GvAnb^r)OWwWeDyt?J2<+&%OVv~C7|<fe+6>1'
    '$#N-zo@3dyr_#XMhSZKw8btfS9Z0#RM6)mue=XUTxn7b=Mi%ACz2k=nVwvi5SgcQ4uS?1urd+^>wC8Gi^=C4kBtn&h3;E#ckBih1KvPALs5I4<&1>1SZC=YB'
    '?>c6}#p=b~ra74RXpgN`)r;wk-NNacd2hWRtOt7)oSf;uLF=VEv0(_xQ(`&z6I!G|AV)zE2M6VnRsw@vI$xp~6EgQmy_h*H8>z;m5qlRa0mGjyhF0uRWNy`q'
    'Infn~8mQ*vU14D;^>tn1zU@Qvb7|YqqsLUBlPh2k{aFm^=*)f&sOj{_PCn*x5@r}=CSql|mu-grKT{Qlefw&PIIQeT)o|8?D<#}lkz6)a$ytl_M1`Eq%B<13'
    '1$NgL>f5Xu|9#pv%F>M2sF>15n72r)i%>1{FkJzCU=z48xM}^`?;KTyPIiQDJ=97n3Y}LvD7V_HJ`f)ZngH{^W%Eqwok%6dumj{1M4B`5)1+3e`}l_Z+P>Z0'
    'jVOoQL)6^C8qv=Y-3j4AYo8P@=ZFp<j+z({terP0x@oi!TR&Wg<RICB(jo84j3UHHHMYa?uj~q?M>Q1x(FHqVM)#x1aC(me81!fOX|#vln+jL}M}n2{q%Z8*'
    'AzBJwTwx-D<&?XF-D3aKxw7|g$MD#beeW+4vqq1RrdQQCV21QV1p3rT0Zr#)^EXa9)+WAKM`lT=K3bFhJ4EUerI`lBWeZdk{b0rd@5v)nDGJeCMRjR`fN?H('
    '2Wr#=iofn74r`)e44AV(S5+G8U@3cm7Jn}>uB-M&!%d^tSbKv~w!A;i?Gq0bNdK&BGR_pr(iEFQr$16|y=pVD9y)%ZJA5(G3s*}-3F{H#bwmh0H0&Y;5Wcge'
    '@h@<s<m}w+Q{#14-98vz+-R(k9M>_5|9{YInLp=a+31p>WhxwCtYeG!wu04NzSPP>K~03?fc|2iNm8&rh9H#YSj<Jy+Tp=F`Fx8OdID7T>2p3dZ<TXTc{+GP'
    'K_Wv>xuCNpY!!HW$b4U}x)KLDk>J0T>u;!TaI-E9Q^2kkCI!3+7=C(2bvKhbTjDgF!#6N0c7<Il*czx32~?(tMazK>-TKqWbz6PtUV6cw*cV53XD}Qiy{nwQ'
    'TeomAi}cPOMc#YyY31l-L(12S=%~D9zgC^o*ztZv#5)N+b?85CYTdfr*_=RRYokV;l*L<={9~}fW7}Izq`EE4{Y*~71h4LXVYmSJ0RB?0x=j|-T<C^yFUVsh'
    'Rr}9&P2z2a4OX8LV=j&<CZ7l^s>8>`{a@WZDbx=iAeZ`mEVEL@tw;;6PR*v#$tKM9(mKpt*ST+m2Uv<xyLDS^P)$<4dhSVF9;~Y*6N@#t+_IShM>P4*3GFQq'
    'y=fR<Mf46Nol}gBFUorJr^MKGtW{1FwL1R=z9EWB^F2d0^9srDgD;g(ts4J*66*OcXRlwr{;@-j8H<}bLG0pk)*C7YW!@iVN*+C9KsEwVAiiQsaCDg0O^Z--'
    'N`{0XpZJC5gBzXbyI=nvHQNdO+lGZl<rDl7nL^DDKUAeK$f`O4S*o@hTcB&OzgLq5yM8q4hul7e+5Mky_b{4<vdS&SC<tT9fzjRS4rN4Yquq+Ndx+^PN|X!!'
    'j^rLfyb~xoVxw@R<g&0*{w7HBKuD#2p~QyS)wz%e?8DXFOeSSy$2E@84Y3OM!!`|ar;Vm>9CoV_J;&<!M+?a&&y^|wvU!XWV#cf-&RDb}Pl0ducUcZUQrLy{'
    'rl1*$Y5{XKDf=JI;dOsBPB<hmo1+g8rN6yKg#nglL4OhL)(@1RsqqvaDAG~Yh7~~{rXXn@)LYF+B08;rw>GS2z16tg-mdTM-o_fa5raPm6yd()MWijFw#Ker'
    'vqn^9#+CO1$=KvT!eTzpM2tQLi2euH>bK3LvD*-tT_#E`5~AJjC75$(o(*saL%nV+nKLe8w(Ngs!NmXkzkcQ@)dyTObR5!9ez32`LQBYJ==q1k=X4@QciXdv'
    'SmOkK+v4z0mX6(hr+S5te`_B+|E+z<M++fX;r#z0GPE4~-kY~)zcdKaugJ&0)j(iBZP8JWn}qXc)%5oCmouuUu%>34YASf!4z~l3aT)^*NHx%@(iS+(!j{`*'
    ')gLXoYtuH+tJ14}135A;p#Lc_TVE0a$s`3noo?o(tSqbEy3p#y4jP8?dN)!psTZnKVs@}p5`_S+sYk?sdpnZyXLXCF0!3%b^-NLt`~E_+gsU0QysUqB#I%L9'
    'b7L*36G&*$L`>D{Q17}MGk=z4u$o^T|L}GlJAyz166yzbu9PQK^?Vh!&|%ozn!kW&vrg#a*|s81Yz>=b|KA_Ma$TIhIO{~$8q9c{)j70@VY1;4AN>n;zpTI~'
    'J_I+X%8E-4m9QCy>Jt4$uyauxi$H3~!r)yBo8|xPH3Xv)gU-jRr4H?9=To!-pw<`GIs&GIECl^qajG;vq|{HiDg}pmVUUlhHE|4`^(oV!glR3rYnC)wY;qt!'
    '&OS8#k<|ICIpyMnM>nJhN2fqc8<fqZh?<EjI6izcFC#2kUry`zFPjLIjnzRco@9vG+Xp@cb9h1%_x%S#Qm%8BHiiQpOo^S<e1X6mGw+7n5FX%pf8ese%y^(h'
    '1@&>W)zx@3fGIfZ4{m5c&a!16QCpzBSo>s#VZNA(keTjs*0n(59xC{|Zhqs>8uh-14%qw_f62E}qwpsEE5t#@K78B60LSTE>_5_l2|5=81G%JZKhi{uuEpZz'
    'O>;vN!HaFYdl>}cUZH1`w=tW#Y079tjd6(*;W<#rv~@*?*{Aog(wKVan!cUQvk#-`YJppk`BL5=q&A@vh`eO)E2^+R&zvczvk^t-lT7a*-jU)~Eu-n^g;1qH'
    'wjTHIX4Nq&3l`+DiW?qgrACLg_w(t+k1t;*{NwwxA5MRL^)^wj{wtOWN#VC-IF0e>dMT%gP6u>vzg4GQLTRrgb8L0iU!sq<K3FtJ^@U9xt~fq+o}oK!#$0DM'
    '*9<lApRJA<{zmMkErWw;-)YE%in!L4p1_6k4liiD_t;Tyhb5$+M<n9v86NkCLsBcljX2gBb&U;a=1?NS;6^f2A58CfSHV$Q5D8MD%tIjBH`q7EJeZF0(O|Sd'
    '1|*73E!KGN`3{d(0J;edeUUB6>_)QNe!IRORcr0WK};Z&(Lp1+qY*^!K<ru^IjpvtpLXkcv&A(FiQ&q2>U&t(?g1W+@0l#g*1dvOvw0`l*`ZI7I^o<RNg^kF'
    '{8!{cjTR5>_0f)3zk+2$&R%2>{9tdl-rVI`+&RE1t9?o`yhH=!4vdCPvdbyf*xaeN_Vh?d1kDEh6^3o-wVw55km^VfEIgblp@u7x%q?<gXyG-dhrD6<c_ix$'
    '+>Mdeb&x}u8-f-l*%;?zH4#opY?`AX2hL5V7-3S~ZEd&y3Nlo!mFyqx^RhJe4|qYM4<KB&whyGhVe1g(Jz5ZA3zfl|Ni6K8jOYzg43bq3>J59}Uv=bYnA0Lw'
    'VglJ%XkoH>*kV=kL2S#Yt%C!849zpyLhEmx7K;a|L_>Wt|Jj?j_j<CK{|Td7B3uVdLHL+zwS&Y?2rfM3B*1WI3@0Gnz_`!pq)Glhs5hGy3BAke*hwUP0&1^^'
    'i<Td96i|2gXfC(7gf#XIk%Y~Ftw?eMwAkK_hC{BCnsqZNpaw*vB~e~%BKfNs?UH#$aQnb`$blo`wouztEhOocaGGg8I<VAr5bSHso&6Xky?P6OG_AiI@ew-?'
    'I|r8z64psHL7gWd3qmAD6r!!;Okmp*fB+lk?=zSnIKZug`VKU+ySo>|Uc?&Z$xdSrdeJ(px8X-?zlB|D)|*5S4zaBMxpRp0;g@V)N7y=b0&U#~BS2-sa_TcG'
    'J4)#>w0S+ZWofsz4oHjA;)6qHZHOt!2mP_Zxzf9p_Mt;mxwSt;m0(|n2#mC2p2DSwPY&!Sc!NrE0rl|5(_c)~h%#yR`En<7=3)vH#;P2LPf%<CZe~gbp;-!3'
    '`R^}Ze@_7|?S`qGufgfHVpsZex_!xp?L-~*Sy7`nLq2q>YLjR|2f1!>4sQ}~-Q)|DY(ZRN{bUT1-v9#&bfupJabKc4I?#%I$})0{4$3Ad0^h4TO&?TIRhJbX'
    'lB>||GFETJe_&}2?9i2YF&LfVd=sX>XK#BiPJiI))ST%G-4Kp~`gG|ZPA`5wyLf{;>ThQ}9N!b9XgRPB2@k?`w4#M*SzSL6;nFF|Xd@w>kp4hkrpO;ev+7lf'
    '9$_~{D~H0bB$8qL8il7s%B-rXJmq{DzyY7*9YTpsc>DhoYx<{7?qbp>P-G@|c^mcDx7ov@>TFcwUaJ%ae~os0iw%X%aF;l8#>X!}TvieC&2}YS5f)FPs&741'
    'NUwxcjbDdt_NoYuqrgm0vJa#5*3jo%bWKz#nVy=G^w%F{D>%%O7TuPbjuM44@z|>^6hr)lImVGOOuc1)tC?@s<Jj~GXc4b%L?DWY@aOsJ{S)i_r&)1yUvt9*'
    'EZ+@D{~_4XZd-BAsY5)Oy)F@0y6ciaSTj$7xHTTk<ivdvHF9gLHCztZyQ_fo4fZex$~)gn7BO8d-BqIVDh5c>_nLqyn9>X8e<_<N-3}<^Xp+y~?uuc*VfBmH'
    'ctDzj(>W(AhFKiEq7-62{HZjW>$J*}EdB$I7XQ^=y5DFV@Vv(PKTy^D)Km^OX1?d^u3xFS6pH84TbVSDtxTLbRH{Y_O)!tGl*B?19IEN3AjS_Jw|fl`ew^mO'
    ';_@C16u)e#dW6c<rDki8ivHNdNEM@4Qm1v-t9(kRT&=ae@vb~r4RhJ$@#xj?(R(y7_{Q4itayu3vbppV7$coqn2=6Y4-OT{jqT4Qf=<Z?$4+_K`odh!qpFgW'
    '@Fs={=bx8#AZ5pq#jvh-9m2DZbV6{aKUU3ygxlj(IreCC3qpiOFNIRvQ<4ABI123BSBs;-%EECJz|qlM!r!iJ0WXN+cBrY%!!4|7SAHs+vVJ8I6|P|;a1WV9'
    'TG$)Gs3h^Kw&baVwvs1yCH7`B_c%{T?CmckYrUWTVNGi((<nXJ%t^*2CT5y)#Kh_dSzy#Yv~chpgOau5A8So2h(}X#({?<Xs@9$|<iu0QlXU|_X&&|Kaa>c$'
    'Eu{XZ_J(kJ#wwabn)!o)Q}5Vt+KAa~;5-UB`$3sYe2;s>FYjg(F#L^uI@xj9y39H(N;%Xcc(WIn`jJPIOSil#bu*)|iI-#t`(Ioq-DI8U6J9$VYrgcgX68#j'
    'D&!PC7q`RwNQXU{ovs(bLd2iH?s;<->a}IR-q2UgYUtnRtA?HU<-a;ai0hOPw(qEbC}}dgfw83urEC?Wg10<cK$qFj#-Nw1t^&YeOkLCKYb%qhVc0sr5satz'
    '(aQ$CX51DIC;C9TQ`AQ$VuXW290Wz*h(4XIN~qhCRHf8+ycT&aZbThzl&_>gyk|Bh5#cbW>J>#VK{Z`X5ngpPgg0cP)1GJ8QoXK>6B^b@%~5|mhsGaF@11C_'
    '1yAjDwjA70ukSNaFKY{sGAl6Pyv|aqG|a4alf}p;2#b#Pk6Hi0%MS2!)?chJw#rugT84<0GDIvKTMny!(KtncRy6Bma3OOVFELyx3jB#@jn<pOuFzPDxdkjQ'
    'w{M$`{d%+2MwKtZOF_fDz^JsxTE9I!s6!cikKj`YEAgS=VZGTtq{poWJiddzOyKWki=XX^->XDze7n=;DjE&#=g6yo&8bi@*dz<1AEG(NR0!mb^KJV;YF0RG'
    '(YL!h^r*d?@WR~nDTc4LOOLU)i1qaCF867-5u1~NQDPKA#DG*wXXBEdR81Tm0ZOEcSwKynYmq2>#gZewd19hjD*uLneL)V2ZP}>0mX=uHpjL1uSA!cXWdSMl'
    'wAoi|MIhNv@F?6<93r1Eva=wx`V|_O#$!Vk&OV@S9nMnq!{PIG+)*}-koAyvTzeN58!ZK`hL|3A4#Xb9mPgw~R2ef-;fKIo(N2@>mV5Xy8|w2dp!If_tPwjq'
    'hw+h|1zuG;4s4LyJA95?v|4K?y9ax*ZgX!>KX32t!1v<KAz!uSZ7XTPTf4LRRWms_Xu*e$EpCQ;U0VR7D%vJ-D-DKMoR#9H35<GkuihXEj*g<uM*BJZcc%&e'
    'ZM6@c-w&H&Z2lwc62JUc@4M4Cq~R6qa3{h8qBO)ESURI6?nHPbY)x?|g3)X3J$~B=-tweL??k%|rKW}tsV>r)!*@sm>@W*>-@yEPrk~m}f~g-wPMCd!9Y4d^'
    'TBVHUhl^X<8%h?zClc%}KP};;XPS6*c8btgFGLeVl6P-R2?2af8PtI<s!-(GU<`c#J~=UrbfOa9F~f&O=H6nZHJ%#O3P0QCUjli~%nmNg$iS|<YnGd4(m$9a'
    'UP|rYeswvr1Ry=DpB*)qv>uSl^n5cjCG%S3;qT4t)8<N)cORE37F0)@F-zE+W%JQ=NcOR3s0qH_9$dcz#u2Yle95s-W`I!BNkk~xr!U@;iy$fV;PGGmDkU(d'
    '$QBS#<x%^h!J~ha`iu}WRPY}()>VD6(<gJ}wTU59WmO=VllU?p1gYgNZf%X+^%R*)oKt;qOT`B&naB=&vgD$iBqnmKFjX)RYG(uSaih*h&Chw=WncuBaYdaw'
    '>jTw0WBGi7V$Y!9>;3N3lISTUJ!T&4Ud4z7vh=|YGP@p{V5&t0b9hF<_&q|~!Ww%0A!{48?9XjL2NJuD{>L82HK3yIE}Os0QVI?BReo16bGLT#Lm9eK)}~mq'
    'd9RNA<re%0WU<9UD|yr4OF#dlQ(Fni;>#fyo)&1K6YAY?mG!hHYw~gFsvUvY`HIK<eIgoO>mvCRV$J*s(OSI6-<icO$^I;?S4Ndd@P%tw9$NNE#RqnDoHTG3'
    '93d#FQ-z-3ug`^Yz2E%5SF-={^zB*4NSr9Evm*<cHsSFzOCWd_Rq@eIgFP6Lfv-ck`~G~Wg&5B{i=}P6bn32;2ggt4ga@gPsYG=3z}|t`9Y`m<1y~$@M=7qA'
    '`wjI*3ra`qzQTeO7F_rqYRth;J5isl;}UOX)Cwe3vC4t887Nt?q_1#1a&i<oM!KTZFuOu`*5NyLV$@=jo?Eu-lR*>RHd%0zsUzWvDiy*pBGC$c#L!D|1P5}m'
    '^o6GmI?hHHz!&{|#)1^bJpFOJKJK4Chui;hexLdp;`nis1bBXV%*$btXX;l0exI5!8RhJ=V6pqw)2Bp1;oXY<X~(I;g4;XXTZd`63Dm7<>cSF&Ug<~52>Lrm'
    'O0d?#l@p{7#kYVx#m?+)Vv#RS0rPmXIU$<<OH{SWtWs+6&nV|Na%_8tyV?PSj0s%X_J{s>mB9@_I3>~mG3dRE_I~fD^NW}NIDh@7pp_(Q#g=mcwkBJod~?{a'
    'FY6FrlIYobbQhGu2-?L09n{@YaI^#Brd`kw#{M+WpRoHF7869O3*fMSy>NFQ79=@$H2F{+F|NWu$p#4VN1J#}`a2esEkKaCe7e?{wy?U`3-=2M9SP1?PB3?6'
    'm3(-gOqhx8Q^A;al%FzVNWD6lgsMB2Q>kz{7?d?GukQUSTalBtIwt5DG@85vURrHu)?H2)vJ&(~kj8J^8N6F@!>Trk3x?|v&!>|`2x%=9=1f9gL3mSC5*}GP'
    '7GHc??+4QV&>xNaSA+y(NwIl@n1}B{o)h|8=!KnB<^<E2u5H@lg%*}OoANd68A1hrX+p*HNTf-NKyl~|PmWEqvdPf3-zp);MLR;}OJdqZ2RLs4uA)QL;$=ld'
    '^d%gNt*0oWV0M`x1@pY`a(mL`?^3wMEK};^g}n&@C3)hj*M@V%3zEy3hKkfONfAm@pmC${LBQ9XGG%=`WvDe9LB#sX2|5~gz_l)A3+lbDZS1PkbtVJUDYYvS'
    '4X_hBK5D+H{=f{`2SfQdT2=FRA?v+4ko8oG<yv(P?)v3n{SGe6d(JVJMDH1b*Yq)`)LD~K(3<mLB0)K&ftCXOCHW?mHLz$dRiJ6D|Ap4R;E$ZP#d8t50P6kb'
    '^p!EUqk!k}<Sei|dYZN0@|c1d>jFXnYX}13fY)@uu<vlKe>xISekitn<`MGETHTB_zOSO43D5qYs-dyEu&ItFh5w1-VX&Mp@tkkZ9wOKVzx33DUc0^5*lpXp'
    ';15vlfaL$;?Zw;E?_QmC*r&Qq5XRS|fp~1N0egUy3SE`)vtK7ehBqZZm{ueDAHfCMRVWRK3D;)L2Tpvw6<JFju?Js7*;`cxLBWbJAyn5R!emum0SK@Pq~~_R'
    'ss9!?_2me&w__^{jD03NBm#kWN70TPW{0Ki(Xa;Df|DVomcor;0HDE5MjRdNci=<CaGdNlb_^~JnUC?jVVv@HmW?I3_b93!?jLS9Fo*2HVaz^Pi)g=o5D9J)'
    'wh<X19s1eidVZclCG+}^lzFP!ZgVw<4XH*&V#&-q6{+9NufA1YyzS8*F`-Z12&>io1p85j?*eb3P%{K1vs;8C6IBm3srR6`URAL>mDOsyyxvxWDsC54jIULs'
    '(hHT=5dQMwlLpJ)^=QtD?Lio!cED(B4^K)MW4X=Rf&`x|4?wml;EaWtZOIJ{SSGS9s1>K1w@TW<Dko&7%1zegBx)P~;{wmYO9dU{%P6Kv-|6>-mE%t)(V^$~'
    'm6gYZD)B-!;8D4RuHvN@K)OLPuPzAMKtNrXr$tN-dOB6E>I8g)6Hf6%PK$m7)mKLLA&+^}8NW65s&g}kV)4ybJ(FzR=Jnjvq0)H#6tEor^Ri>|CKN*={<|IJ'
    'UwoycpD)U@eXhm%&oKi}#p<zX%o9^@y65qW&=p@i7Ff|@m+%_CMt4ocE~y7FLkI1hKY?93|LyGJhgavnN7WgT4F)6>&#T{{2N%s9xQ<S5?%>^bs7Q>?Df{H<'
    '3{xW3TiXq08Q{eY228iw9170K1S;qs_--oL6oUWXY&7Zw7K<9hBPrnm;am%F{Q~4AjHiFd5N72K`r+Chl~{p|3PWgw>I13xe!3z@P0p&xi5(eFXnHprXUhy#'
    'bj$j%k6wXP)rV|=zH&C=guz5WA6NEJMdKBvzxeuQrr!B)-qkz(&?7e-yn5kpEw;elp=%f(liS=PWNE=G6y1dg6rE1ytJBx7&n|ke-&|ID1B4u7rDCN^w_t_t'
    '+)DS7elQKFbP*(teset)MRW@E>J^q!Dtrl4P*AD(di4rPEfr5IC9ol`b52RVuL4zSg&?9Ue)ug_emM|#8~*8P)U}tCrLmr|Za0Z06xPdM(G^x@uytr&Cg!q2'
    '+2|{hIR~q>#?i;EwnkO2E3#mfVY+<`@A7dw=7qdlT0zjBvonb3($?$oqQU-f_EMsUlMt|`VxuZ}9YBvc`9MPd&)&xtnRRM%w=&8z)qWCPsSzv6JRXxlsBfm0'
    'v;p|+%6_I31|V{JKL!a8|G0|1Ba`D?^V$b97K-)$1~}DrIgb>|f>>exq2gyjB)uW09%P+%#1J`AZ+^JnyIKv&4GjC2Pf!?Wy62qoFio(mI|+W!BLgn9#$D{u'
    '8?yzG;^MiL_SFza??#jU7`V;pVxcM+X5$g!{8XiKy-5)G+GREIvvok$DpjvG8^8|2v{#t7lZ*%2il`GMjK*Hn`c?lOF}}eA6^PlF^9`S=!|ffJiEG7}#PJb@'
    'Nr)16l9-Oe8#9P{O2zWZQaHZ&BA|D~;cUZwLwqi46Q4!Z2}X6o2eCd(gaX9m@+i7u&`1-7W7~kRMrYRfQ?0604}5iHGjB7JfNeS;vbVc*H4JcOaTj~Fp9Dgn'
    '%6;Cv<580&W?U<gy~bLnIk@R*YFJv)HC<j-P;RIsMA5qrZP$|^8=&jO3qR)2s2*4%$u*ywUhdFH<)K3(v!N-YIet`IZXS6LR8{MV_<E?RGe?n1icqkIvS<e7'
    'vZ7d%ip@WJ1&Cka0(fAtA-Iank#%7&j0C1MX(@d{!rT`khUR$er%ECAeendCcXxi6hpRkI0?}1%DuJ9&vbrR%noK8kNhD9mh3M_29knJm8D@I}7JKxu&Pl(;'
    '{7)?JDRASMq@J*`IiDCKBqHz9M_tKwbWQ{BkL>^?NhF2~LT+uV1;b3Ciy0{<m!rE3<3^UNnFKjW7Z)7;h0sfNLak!>Fr7Odne)LsyNB-e-n@cY`QN{uy?IO8'
    '?N+<pn`iG=1XPPJe?PzY+u4PF$Md1SbF^L{C%_7z^E<KJv_*iIWi=R&h25dx)3+~QaUQ7ZZn7IE)jj&}zWjHOp5T9X;lDQbu^9J;lzS%0F*#R@Y9F?K{R;Pg'
    'jej=rXS3_oFzYXGFv&~8DJT|RO?V^q=DTfl%D-DJ*&0+;Ws}?NAszScu7>>xE9z8rr?5(VL><8M>vWg-*yIYS<-bNV#FxC`;>`}m2;-mZ+9OS|oxJJ*8ClCi'
    '?1>zI5<?PpcQB(t-AZaLaN!rCPhroDlwL9aC66kG_KE%n{UBv)GUp{F$zz=VM7CkH9QDVQ0NArq{3tmqEfJuOP+(4d#`3Q!Jr`xjNiQi~PKAC{BwY^8_{Zdd'
    'To2Ty>pC12vBp;XLt^F6;VIzcew8>)E0h$yV!x!scS5z329#+S)F0|fTt4)_0MSE$*u@ORYDT;eA2lW0JjWaXa-jRs^-73IG#d?W(M=Yr+*S+TA3h{hRoa{H'
    'wR)q;Y=xI>f9`A+B~ajoOZ9o6?-D&tnx^+ZWaCtCWG?mOO|I0TLibYq9+yF;^ID|=s>J?0*1V!fL<<YcWu~m@DW2%6zk!}VZ|&5Y@iUOJ_M3-sou<#AoYTN-'
    'x~nH4+k9|EUl_7I=wrYwvb@=xVl9Vkq#`1mEf#3&0-8^rgWDJc2Irn*cDX8;Rv72dO(p5XJW`$aaBm@FJs7X(3=(@2DHdtlc75#8ZlZZN(JZjFe|mXwRtajQ'
    '6`z`1>h+^mQy@moLlBj&I0;>aYL*r0*6ikLP3@P(T{8QLwnn|#O}Mt3De!6PSsd4zA(0XnE=^m9OdlIMH{N1IYfWMXxlty1&FZ|Ib-kQ*)fJ1aqhTGV)xEl^'
    'EPhtNsb5x%Bk?-&28){xrn84_1k%PoB=54?r3=)uV=1eldaDDg0{k|uOE*z}baj=cFtIK!3D;hDXunOH>YhvKiV?>1H@r#|Yeh^8Eta}nV374xF{%2lzpU7|'
    'JS=nCEQ9zm41=OS)46}?ioBwpev<~Al?@*fsAt1VL?ndNRmL6Rp32=VdP}8NmPOIJbuX!T+@D7v7pGw%nG4BsO@Lm*fw_d6Y&CfY+rMD}#L*~B3NBl|hpQ{)'
    'r$@^)aKGgo{{lA|HsM}m->8c$myCMTxwcw_eQ1bwx5MMpyP~k5;u_$oO~|_)o+=F>N6kvBNE=d{OiV4mVQ%;Y)_?~~b}hV;Lpcnviu?ZfmKZjyODS8)U9Xa;'
    'uaSsw#fc}QdX2;uQ$Yi;T6J$(Y>|uDxz1K|1TXfM7>c5{mHusX-NlAy)|T<3IHf*|mysv=TQ>L7y;lR@s(YxXiEG7|q<yC0i}>QaAE)LT0!PB#WfuQOq_0-`'
    'rLz-r-}?ISr`%*nUV^um*`lKPVwOdfx7ie9GPL$XvnKos&QDEs?l{%;1r%j2RVSXsBIp6ia9MeA{_54)i?==d^79k=rLxjFlEtrSOUs|mt`470p#TH}hnMcz'
    '_myq|N#Qgrl^3UYQO26T)?6030FM^hp0%wwHAZbgUQNYV^#$sa>}E=r^A}0dLA+J};fP>MB*6uV*MxRGo!_B*(`Yy$7o}lFu>;udVs(8z8jLtF%Ux_(*gCsD'
    'hxSNohh7?ir@y!bfv3CKCGyB+P;*;)-18O?JOb{4cWAdPuqnZB?Xx1~H#sSokQpkeHEU3(y~$~2jAt&CN%#U+mB&`@UMOlSnxw;Y@aScnOM00WZ_agRqu{Wq'
    'iqm!9%juBvmbFFhJL{{*UV0c+19zTX161pBxUScRGD}*Tw$#<6Rp?<wYtlX(KHrIcJL}K@RF)mBEXzL5`jZ9gxj4CbQ-F}}rwVq7aru`BYfrXm#N;9++CzU%'
    '25Dfbw<)laVSP9y4;ff>r7T2?f)35xL!Fc!3ov|6ra}Ij`{?ln|KEoH=Oi4k8LjLD%>#JRL^~b7-0wtvtn7Mpy}WT0ax7U*GEO;%jlt(6#<QO8YP#Y~1mDZ('
    '`)E1mBr6^w59J}4t>zeomPJ)^CTL2^F4Pi^-c4{WxF@1Z;2~?%Kj*DpVthTR5h&i4Qo~3-`l?v&2TKLsDL_&zbJ*EMNX-ddyWvdMtjAzC8CGXtMXI~;cJy*7'
    'dw?Od7#J*Lw@%K_La4twF^n3hL0%>rjXqgOapweB#Tg<f;SM%Oi58oFW<&u5qkN4(ywTtC9us2l$CTp)(Yg8y88a$Je>>})y?XiMOLl@}fd($ucPJe4YgY#f'
    '5-(KOZ1%{Hl+>X55t}7@&<-X9aNkXDB~bLN_Xh4bv`Ptg*&z#Yg~Mel9omo;4wtQPv}?tL%Tj54MB%dV>!9(OYvn*Ws#lnQ_?9X@{~i9`p}&7TKYw!uzuFWR'
    '>xyw|)NB-WHI1ILqANuyXGOAUqanE23^|IMiFR7pIQ+6gKQ*N?_FPxq6Hy`)$lql($k_7~u}!>2mKZEL%D>cMum!#c(iu|KEjX;WFsnQ4LCoSFd-hdwdAPIz'
    'xV4K2rJ%B3u!NcfP`Ps{*p;xO@k<<+2u2AH%Zc`gYCMSpLJ+roD_TD8J5BkC`Y^u(2+l)1W5yYIdD4l}hCN)L)P7{_h15+rKp|&hYdzA-Pq&@u1I_9!96oZV'
    'w7pSoaeK<3Kd)O`FXY<U!3qyk+a*&PQ|up{@c0c`xvY2u#j$)jVcP*El^o6)$Lq<~BZZvjB(w~L+<AEP%{K2&e|zTO;kCXnybE!zrhy%mXDJn8klL{5vi<7x'
    '_4gIzTTG-FJ!kS(N!03fJB3n=HPJ<_APElbdY($z^NgDREK)Svf*vwHJL-QxJ-s%>`F!JMszR((Fe$gR%M_})zCD?t$Bc?Uaat>Hhjf&oP%sS6<O`srd81FJ'
    'J<4%=UIKfK#f&8`hm=^}Eo}TQuxG{kKsYey%3eVX@%=`l0pGRxAL@_;>KZtX-eq27kzRMIr?-_rJ`2uxUxfU+4)it5d%smF=p2R{vrbWZ1z@z1=OrHWHRgh2'
    'sKo0j=5->D3V2^abQDWAAzCVn_SNcv><*c5)Ks4HDx%oEyaCa3(GhMB*<uB8^=^(VEdr-vDNL7!4uZr51FOxnN~L2$Hj#MRsf+?~R2NhqGo*&4Lrz;b?>aSl'
    '!wf6-jCCUm#nDoC43jJJy?DS!r);bj38Hln^@o^bVk!`=lhs1FT&ayFQ(!nzo>B7%EQ=m90<^5qO?bqqKapF7nuUSB9nB(CVG#HEw!}0KFN;j`^xc~mzbc+}'
    '2jln#t4zIeIM!uvGG)!bGTg(X1x)xj>&YBCZy2+whw~yl>s!Z~AMIiU&7S<bFaN^xJ$b$-&t1blRE<l~BQ*tKLRen7>W&K^Wmh)+$iTH9+3Kr1hr+Vakh&_7'
    'j}N2{fqxoZg?#6Q93ygO@i(r5-C~_K`_Qo>3pho$%<6AB@e^+pGW-**c<Y${3qC8g?T39+$)WR5Y4I(G0haBSz?ZGDd@Fx}G%9sB2)h<=Y2{w9rX@PzX=sNj'
    '?<0^C$&HV~R}3SC+)v05$^rDQ9|6|vM1tU$h#IRgIY9awTHw(CkxjM4>97sZuwB&iH8mnlhTH1Ft98%*>aDq$Txzh+(aPjJat)l0cb8+V)J}z~Wnfa-$Ivl#'
    'eyv%;G(E*Nmd{dwRaGfljddsJb)ipPBPK2iw@R$7u+H2E$Zm)~D7UgI=W@@^S}LUD?Uq_{y58IPLY!8sEmU_MhLnr?E(&(wadf;~a!12g8Wmb)ah0`THu*p}'
    'JZsIfs0@u1|LK_)QHM-v;8JohV_O`wg2m9B1v^$fZ|di|3mjPko06P=ZJ*+51!2ihV6oJ!v8~co-oDaF;w;i=zqzlLB_$F}VmAIn=?r?)YU{P*)=A}w3wx4s'
    'C3QWhwQAxhuP5eOVd&^^^5IhbQme<D8H~94F^L{xv7$u}wzabCDkf8$0-w!ap7gr#w(VN>5zC|9ny&+E$ZXja5RFHe6L~N+P}d$V6=JXX$hfv>yx2*1TVhJi'
    'dv|ZJFk-cibS0ME+HdVr3hAh!+?Z_B(TL!ON<9z6BH=jC`;)Gx1nY38lylI1SThNx5oH53?@0vZifulsTT;bOrx(8gPn4_0?Xc=>zyelQdAS{@WLjMFGwI=^'
    '+PtfI=<cu>^GYC5m{jJQ>K%)jL*hQ>h}#2l?sTpbRb8n?O-_7b%}>a>R<Ok_>zZ%&BC7KTP_LkUOI@-`iVCpOW${nUFB7p|7rLV_Q<mOB4Hc^e-ab+-@Rg%v'
    'UyS>!VHUBSqQ!B$9hLRMvY9ayhfZ@M1t{Ce3>6U3IVuFuLVpL{CEsgON_@8(foOs`yn%gMJReYVJ<7z;<4Q0%xH`;;-i<gr$2|K3uuXd}PJ2IGod1j&lN<c='
    '?RkU;ntx~v(R!<~Ed{>6ILCa-`uBIg{_q1y?(z*1wchuqe@7v@$&X%~zWE6YG~^R4(X)1lS~~xY#O_a9uVLYT!i2jZq}MT9_tu;9U-c7uaCZ8JQt~z#{d?>8'
    'GyYv~N~k3@%KbE0t<@bC*bQDQf@AEc@^9XrzSYTksgt5x__Q_X_ZIhk%CUsNtMHSLkM%(K+-ztb5xBqkMQk~m_?Gn0R|H}i+E84Q95~I_ye)#SnBT|fPV-En'
    '+l$&koO5amN*o>@+6FRsiyH9i0^VY(#LmX)KNpO96HNGtNdxwq0ivN)_hnYG76VoQ&$qX8z)WHor&Q_`4L*OhE<r#bJ%BwIWCX5i%*+H%H)24`KyLcuYv?sS'
    'BjTtcj|LgVL|#^@L>+Aq>My)^@bCN+Q_d};*qiBKfV;8Z5xCDjdpBcSmH~ufUUi4vaAB4;W--O>4F-O;+ri-S|6}jnyVJO`ebN8#80R}w$jF6?3I+6VY^3tI'
    'imk*Ru`M6TX?L2-AP7npHUb1lvf9Jn{mj>T)~W(zIi21oy>}8(wQ9ZBT=V&xszg9iBUzVV>Zr*ivVupTPc{6!hq))|_2zIq$UfG3aqOtZU`nrH2^MqrLf}iX'
    'D;SI*Z90)$l}ZJE)+tZ5LGzr?ugIf`S-U^}fI9y8gRu-at2+t`HB5&LFS(&V{)oj9;g3J4wLh$c$GCrOm>Lbau>y*XB@k+~8mv!NjyFh3Tah@>3UQ$N^MZY('
    'S5c#_@W%rF)ghxPzc^>{<eUHusSu-qSzgw~*__#COY96U0XpaT@RaC4p#qv61Q~(t^$Cahk{vJ@8lV`h630SA(WP9xN-t8^^q#`yHK=Wl-M+wyr!F8YGjcUT'
    '6X+Qe1^t@+?xaU~tMkP`;Ar)Y6|xWkS2<vq5GmB=4?BS@i%@oqW%U4{7ud!IRpUHu($m{udh-V2xQsu-$aoLop!nIXdRCD2+-?Hbh<nrtn8t)OSmjAxMJ)z4'
    'SL5J33txsvHa!hNbXvK!Yp`JuyO?Gv_Ex%U?NbnLn?@OCc8Zt9JCNT56={{+=Fo#tJt-miu6(@EdEd9Tiz>zGZ09ck@3wLkV9@>`>jU#xyBHyTv;Yu*P(8(0'
    '=uI?U5OzPKvXT3A8)HSFID8i4N0bL176n?wNA!`Qbv=n;mk&%dFz%UN{+d?49^|-|;>~jg)354=so-osbbNZoY^lD+;`}Y_h*OCLJjKa?f9M6v7W}0>87u~q'
    'Lb5-bOc@cC@*VLt0s>qE)t4yRc8Rp7$OPV?0~oMHAb-;D@#KbpP1A;xl%0B4Qz}ZL0trP#3xB5`$uGjolB*YcBPK=E=l}5s_XjQ%uK$leZX0kN4cV2Jh9TI2'
    'oXqZzKUANfRE^f$nC@h0wV92>p|U}2R`B9>fD+(T=nOKuZS0d$v7xH228D=>TXza97zKv&G-6sIRpxuGD@B5ID@$(8hMou90*%B&7~nHJA@+mk!rDfxlg-)9'
    'L5xG&9lWfog|)uPklpc5gqk(?ih-xtXTr(tdk(-ioc@P1Za>Be2&<(UNqDes&ZjAp6V|#^!Zj&$VQ8CZ5e^eJzW5QL#IjOD1ba?ME{JaS^!YCgfByW%)9#a_'
    'qu1saTvrGfUx~k9V7ia2$hm=;vOdzYr=~xEHxSw-P#hL2G=pzJ*gBSsQxl>(&;j@lZby8Go8p_)KFD5^)*IeK?rW7X3XTYB1UI4@i4lfQ;Art%_U-cE2#Tl7'
    'CQdA_EhdZJ$hPvLno==?qOz>GG+#OE0T+3WsDONnY5Y3ZQ%^LC&TC?U#@EWD%Rm(lg{!o?Ndh7U>IiSf#|I5ETDr@!!4i)?oJ(K}HAFgGe&2H)VMg&!<Oiwu'
    'f-=!Geumsk&RMX6`iY9W+*pI47y~W!!HWmk=!<ZS4G@K{eElTjVOT&%2+0dE0sO!m!k;KUd=cJHY0rRxE5iro8(?|Jg%Jb_#)41_1aJ5Otk*2lnu&&f!rBj|'
    '-hfj-q#vJi9J=mqC`L%@bhPnP)H(#}pmjR(ODlBbw@T;bs&djsQicn!rI5UCN9xKccI3Iy>a5;`LWQFWw2miz^ypFSVx$Hz8^e*8N<P=|mu!7Q(_Q$kv6aBZ'
    '##mQmHoG(+I%`w}WxP?Mvkmg2=&iNiUApVLn3g4Xx4!81f#K}l824)Bv8YstM2(Z&TZ>d%wb^okW%c#Md497@o_FY|B9o>0Y%FC#KQ>fyd5)VUps%%J)K|L('
    '1*(|(POFG&q_oicd?oKQ*?4mVJ>JQ|>K+&vPg|4Okqf`LKoYvN)lRTi>f5NfNosrqnL+M;Ll^*5`Xj}dGSVa*+_@{Pk{(O()<e;m;fa$?t30%GQKoF2q*BGf'
    'vep@OfIfzpF~S1-fZx0vC=gUgN>>|JjFgL-DJ0#cM6XFyf5dot@-!s5+v7oN3=P_I2r74lrYzLxN}$pfO<gQRqt2lKVO!1MYHz}mgVnF@mW_V5@IkxLDbpNz'
    '+~t+f1T&46!L}0c^kwxCb0VxpDv={B>#7!v40jHVKMvk-YH{R-BpvSURk)mYOpN)W^s6sldKF?|tUwqJ>rIWVVIx}N&cr@U1U!U!*biUz;ig$C72ecnq4RLU'
    'G%8C(-euv~8>38F!qH}e=jN&`%ry~GTijl)bg?`Cv-BM9_S3fg0l!wqxmk!yU-Ca&eS%XjUJ2ZidP&y(ir7tnms`6Pt(38F$gOQc+Z-inccMcSN$YPh+m1R@'
    'oiOEEb~x5Q7~U7kG#E;`vi2F$w<cRk%?-7+NjK5l24}dPcUcjF@hvsrUf|3qi!C}0ZZ%*=QEo$?rjAgf8<DZ{u6QMr+mAHmGyE8t*zL<jOpK<@zIRHuh$Rza'
    'HA*P987+bS49a*`qAH~^kx%ou3&a6TKIHs-v~huS(e9PR_f42iBh|v@zj2zEgaPDuOb%;~or0KYnXdvWR!qr^_n@tg5B4p{QlJ=zR5;*?v%KNqnVG?`H&0-q'
    '%Q!EboMJtN<5Ca@yF*UP(pGDw>&~*77ah}rG-7wSNbvk@L=X59QT9z0oE8|-&6NQd_3jfTSU{EPDhW~z*ucwfq$O2ciG_gcQY1mHY|&$e55rXn@wvGwqCN%d'
    '=1}(B$u3}0<XF`U*ELU?mJ}9xjpwHm(l+KRRzgYf=JK{AJD8MxP<$C|Z}OmRo!Cv+2yLA}oFl)@2Q}vN*a@$yq6sVVxG9M_)t*$V5+afxGE@UNQ^S#p9Gok4'
    '@V;_aCbTtGzC0b|hli>SZFGvZ<f5Eo#!qnv^sg2xtyRuXr+6?y-yK@z!p4f$*&CG!ajeq_OKy>Jf=<?0+$QWy$nlY0?cPx{+e=waCviYqV2Z8CT+}6MTk|q1'
    'qT3{d$w5A!_sB8nEAkJXt%CyuQ>~%rX)4KO8%PPM4^weFm!drt|GGL4v@Y%E&g~_o0aoHYYJfx~Ls^b^{Ex+0i0*hBNRhvfE(2S}Pp}i{Y!Y3D4qJe*V%or^'
    'JhSZ_SM*6S`P)JAHyTCE+J|&AlBh}Z{%Wf5n$mLhl6{6LaJyQUZ>8YlJE~!);NwTlmXnE(|M=`H$vMX|Z(k?RvejVXq?k53tNb4KIr7oy%Qve^uvD^96~nJ)'
    'IFW(XRTtv$hArNGlCi0g<U3HZ`Sc3cSK4;yp}FpULu$dVyw2;rkxwV(7BMPctzhz%PpY73eRa8JtDs;YQB_k_TACHfnUFwMq!lwF9sDI+wka>y>*MFzX&a%F'
    '=A5|#mhzNS2vPpG>O2Cuet6L%uyfd?l+%_o6x_veo7#X2XzNe&-99?rf_X<DXSA!(&y!c(U)hkWem-+vzc_kBPafD0w3BypYt#Dj`J2O+6bM~;`TWJNc>D}F'
    '56QPjM|3C&p9lXq{N)$4tJ3%8W1l^QzZmi-U!zkK{+4#BB~|m$t6z?uzxsvh4pyWJ8knF8fdK&pRuw-vdW*mGxG>@hA5cS|)f7BCdd(i`KOOvf2o<-WMX7)X'
    'g}&skpa1J$2UM2ct13;;RMDIt_D{#Zy?XMjd-9rH(cP-OA;Hhz4~}1TPu?6IA5v+a{Xn(PpB#3d93LLMG@bHhS<R{$!{Hm)NI!GMYMBC6pS(Oedh_i0VQI~Q'
    '?|wcwetCF&f*bAELmup^yCT-BVSDG}1Is;sGTZ9TGCAa8CB|n$rn}ek?)CN~>je=2rP|9q*M9rCJAn!r-+J3u9N!FPy_*`Lxv}y>NkaJCf~iq<>hGc*-&T$H'
    '@)$F@QUu#%>boil90Tbd^d2Q90KZD2S{z7ot>QG*$046p=%Gnh4L|(+FYG<TnW?xIvJy3w`;0%bt>Dm9PYj9hQ*$lrhkGeu32zNJA|CHoHT&%PY-0r7CeaLJ'
    '3rD}_x@CL){+O^sj42M^7XSh|xW#OhTL&UYd|f^a#{;q4u{>fS^@~|A>{BbjsvV+_=p#l<5tJ91ZV@#4HI)^6QDDppVdY3!4qmOqdSRLHuF$;$sN4FY4PBMW'
    'I=SBV*Y9l5!In<&$LVB#HOpM3olX^>M5nz)|J(|M!vyvF;sitQ^e;OTQulcKN1<`(=5yfeZsl0EsW9GqvmT{xMI0|iFNqyAuY7IFcx>%tOtD4%K}}51uR$h|'
    'T4THXr_XU9vlT&x5k4@M^vMoAY=7t|&lzgeiA~RW9EH>9(%JTsz)?<Kf>NGs>vT%wP9Y~BTiA%+C(;j;<I9Wk8rh!|=tXc2-y2sqSZ5usLL2kzxq_M6|2n>4'
    '`kws~XE5Gy)EPRfL8ma?Qh`?(vEk?yHdMh*L-*c5Z?WktyM{8@h4nna=;Y}7n2{*58<-NX{f&>Lm!mrG!qg<uH|WM>-BVPBJ;~#1G2!9JS36UDMS2*H)=b$R'
    'P}z0F4tq3r9u7Oc<)HrT+W3fx_f|b>w!)eVb|@oLN}l&13karYBK`yG^*muh%Hko$An|!Voy^7wIrBm#LFMl4-OOj>>_$1<aMs94h)BGfEZjA>$>k8E!100>'
    'uNwO*uq2gMp$4~xolu8J1<=!{Zx0Wj^5!5TQp}*?Qe0W?_>=6W&8A13s<=b}%wq`{F6c5Zs+*PnG*<P9)!Z~(s|P9fKtI|>G`id3!5c>Ln{vgq^c!{{R~s&='
    '27&FSD^(a=RD4%vDu8XS`O|zhL%4FFg5{JXAcT<0CHJvN4o13=vx%ZXg|Z8pqgulG7xLTI(Kil|?vUVgHP=2}7^=yrv_#Kj%IeY(JXNd!hP36_d{u68GxmBD'
    '>^(QO>Z(a>Mqu&kTvNQ(`WY1>eQdr(FhC=AD4R`zYpoxNtMbR*+1*lv#rFn!)=@2&YnAi5TBBT2nsYd}`*JnxM-LwD1m=Fdm~l5F#VN_SD$E<zbDW+U_QO0|'
    '0N>TS8o>n2wjXq<Fz_0{*OCmzt&&`tckc+E45jQUCRW@bi{HVk*}C|gjfB<%Jz;mY$Qk^NGH2yn!{iy4%PIUNz37c^YsNURWsJgP{k8C4IUq^FvsPkbCsx;m'
    '-o^P;#_M&<wQE?}c*(pG`wf-awaK`U>uUiOAlw|wT;t8ZHg|--mNdbQ@Y_=OVmM+t_D1V=bFnue2Ow+{Mom3$l{@Jb_`8_y-vdZPa8@Z~=u2@MifTt)$C$38'
    'C7Y!%pm<f+#(UdlcDL&(lOO8Yg6Q0mJJC1HNll6DUdbL^x@#^=?o)?K+vJ!#XY_Yvy@s88SzbMD+^}iR+1jQ3^a#O{5v{*|t>s%|Lfo<CP_Yrn1Ad3oi2Hs?'
    '^E_x{$QL^*uK{+VY-{Hj9wcqR%#n@JddVloE+Fe$KFSrWrAzFbJh}p2g)Lp0TY31<WmmMpf7vzpS7l<bHsTN`>tA-AaCLBPbxA5mzLhq)u9;d3kXUxvDEcbY'
    'pEdZ0P<wuE`+Mi><a>8MtQYo(@65iGa}mXy7=5Ny&v)St@7!g)LlVWnwBho-A0~#5>ECS3|6n%8V?qd`p@c8EZzctswQ*)H<M>|KjxX}IJXNuZ;=+-X%aa8?'
    'zV3~#GNm0VvuR<66H<IM5gMkLzz})0s3Et&ND#0AO2#XMxkg{O?cxfA6*sCmN9jmcO+ia&Z<$|X_&^!8P&+PnM3TsQr0FjEyEfvuY-cDy%i^i#YA*FWFJE7)'
    ';ewWLfR6FRl7Ah}48yL?U9&-8Uh%v>=E;&;Vu$F8(+|$LyvO6L;IWN=hJk(sGE&ZKuG=ooiE119VmMM|_tUr005NyaflJK`dUx$b?~qkOKVA&k1q#EL`f0EK'
    '0afO`8I~MeN!q>AH9osyU{|wCtp3I2QbzF7lfQNz#mglRX?_V|S@Diz4J6$bL2_%>yj+B&rg~)O!7YeYCeqV*>4@mV$14qoItjO7+jNXr{2RJ4u%hL4$OMAC'
    'TwY$JqFII-TfIw{miMKoQ#F65yg@q4HV9A$;vlj3cIS@5^{JVh;KH7oRV^2>^WxnIgA^nRrAWdvWn71xKTpCNWoHXptL@bYYl@DX37qzixL2897oHXWfhnzp'
    'OeKi7H*uYOinWw?6=@0<ojbYN8w}`Dh?g{2$dVZygA#lv7FFj~3c4WkrdcJPj}Xx-(L2zbFR6kJHsow;!}*77OmyA%Cveja3om@_wS(dmj+QpRiVor@6d@G4'
    '`ppL=*Z=)6YYG~yzM==xvZ(DkdB9v=O%@qCz)WVt#jRHx^A~hR=vO1?G>`L3Ld9gZ$Obiieu&M$mvNEtTvQKTIX7Grp^UgMXjg=zQ?a6N(sJe8_4cEJ?g{wp'
    'aDvd!cbbo49?Ba7bb{l1gJW*3L1sOt)Y1sSoXJr;xt4vl2Hg$NTv(EV5HV$x%$4vIJ`{P-x+@J+frX_uYh%V=&gkQXu^OX~CEF9ZU2~rSA5v)CpWKY~hw!)i'
    'o#zx_+;42RCk}Sja9H$T_>HFWmNKKGm-5XRe#5^D$%9h<h*#kf4N)<f5hsHdW7ydBFgviou4sosdUQ3$h-$Ji<EKjP@OdftR9S$Ee+E_yQ6XPX?MZ`9S?ow7'
    'H7|TLsW9k{g6qq>^xE#Ymai_hRw)dUF+=%JCpLJEAQ>t~M&<Qp-`hFkkKRnK5V7<+o1Kj&H_>7;9wLi!x0D7`Y~s($Y4EIj@{AHsH#y+|{08!3r5kuA4B3ej'
    '9il=ocIf{p(EtaE=&+6lNrZW$Vk>4uMPlGP`2TIrCh+Xu^BFwz@)JCB@)MkQ`;*Zq>o43q1?QAO#ee4H4>)(y6r7WLh?PwspFQBbAOHeh{GB+!%mpJWFi4J#'
    'b#LJhe*#+5irPq1CeygXS(?W=pnE~IhrVYY1s7P7c4D&G$r<Ol|10Czf2Di~_YRL=l1Dm;YF6fVjhDO@K>qpvRRH<VRsqO=_CE?B9~GZ@Y-HJAjxHw;rB6vC'
    'Z9~PMkA}ZIzlh`6U6g0Uwv?3S8?o9A<{incfSR7WXCf(x48o206;Xem{q<0PpM7oA-)E)q9U8;;)91T}ZfFju5b^0*QQ*dZAq4K%!?^t$l{SP*t0BHzR}%$S'
    'I++&$mbP0KIBEG+8;l;sA~*?rk!o`sW>M$Bbw43vW%cM%I|XLB-0O8}HLzJH4%CQPtM^YLiz%%|!qz&{;NV6c2~m+s+mvR~M2mVPXvkS^8F&pNv2uvFCY<!q'
    'Bl6p&=JKS7YT6e<NI$+aUHWDn^wHZpAjZlrEJoS0km&LvhmS|+)lX=e@F{<$f}oPTqlox`d#Nv!O^Xv%6hd=`C*zFH-05U8av)4Ks3;v(t5L%254D)zK`8cP'
    'z`D2Ooc5aK;nT_ZN~WB1LJY!)c3S(9QU(dCy^gyxH$S?ha?ZM451N+r)_It5eIg3rgcUy*APZrJO!xD9X>vagZEjUU4X+jaQ(zo&w@{$Fp|!<%v?q4GFeJo)'
    '8fteb9OU(~yczVGUSiS>a%Gv<0yFPbXjLcaJoKlqYg9irU{5?2&gj|U(_n&vX9kPM(Zm#K`@<t&1r670%het&-(3pa&QUOhdP%w_<VVyxu2{7$U-xVDXUPES'
    '(VspuY9OK7a+*34v#Or^Ck=D2<ZCKHgVGAd9tBC>)~?C?s<(#InBE$HD!N!G25bd*v4EZ2T+%cm2jpH4vH;~?5ib5xkxCnOjl8gxb87)1EOBEk_PV=QAT+g+'
    '0%j!Td&Xl_reYOp=nSI>8f^vV#&QtPr8c*s@hpob$Okf9-q{g%N%TT72%Mh7%OZ!HqC+qHu3pq@pR$yJ!!02R|C0dXoJqMmK-{yxgy{>f-s7XAml_`qaU+o&'
    'M(-w*!Q7<a%OWy(vCpBpjqaAx8>^p9CKrF20qo@1V7fiz-_MSIJ0?7~t!5H!ZNWd=F~1Q{rTYbI^BhOHCCgwnpLKE5D5DhoWHCtp4BMFSv%hUjylh`hU8yVo'
    'YU;`o9iP$f=?xR&l=aJ;ZqGrMP-q<b0BH4Hiu${V>}`uxqw)*%duu3P?_c4EOdM&i0_>Yz*-|6`tSFA}Q@2*)s7a)i+RsO`T*r=7HF+Nr#O{t_PFzH*2<hd%'
    'yov7SNn}k+JpcwmMyBAv?%;N6wYA}RyiYt|ciT8ws>-$PlLfk4OYy3u^Tu-RD(=lqW5M)SoAAd1;=E_h3?<48M_rv`vflEIS)w4gH-qXb`dSZEgcDBSDkN-t'
    'i{qjoQq;wWD4thmv7QD~H?UJ4D<gV?_q{&eDbx(D3g^ZS>@S(aMqms3ibVhBGaBZidfgpcqEU^Dn-8fTihJVex^=dtS(n1q&?mK0*4<{fBXn?o7HD<d6M@d4'
    'Z^J?$y{Z>hOQ=-OpZxlpEFW$@SZd2#{f-MN6W`>C$KA8V24=g3Z5I^OKk^$X)n(HH#WvI&Cd2V9#Qr|%O?&;}0=4$dhA3~X<#IlD7$@=r3utw1BB=XE8eWW9'
    '(rmPwzt~pwuErrqdfiXLUNe(x>uQ};rlk?IP72=LoQ6em@A`alp2s39+n4#9v<h?a^zV{W$j#4NPy^0nTW3}ZD@ExLShcA`Ra&LB8h*X&+f@7Hx0TPkqJz^d'
    'vCFrfWAX$!4VrJT@nx{PCGa1}{!$foG6+kNW~zD|j<%z|n-GqIuT`u9wH3$S&^OUp-wv`tRf^ymde=Qw?$m}8M76Zatt^4Q2h>eEHvv|i=o;bz2lhgJ+Ddvf'
    '0zN5na#>k<78pgbRVAl9T_38=OZMSlgyeK=MlYXJi|IvnHD<UY<&B@p)ktwhArLy%UO~R!S>-P^-&xO=(~2!uh`F7)vqDT)^Pg3SJv%&ps<S1$n@r%g`~h~$'
    '4g4GKMYw1B=My-h5y-fx6vJz!I+udes~KuTGE!j$6l0}YvGZ&;`15ilJbSvuDTiQ{9&O2kH%FK&@j*j=9v{4Uj!&AK+w$b)^H<$p4oHvoph3{h^!UZm(XT%p'
    'Ji$y0s^rmY`1Tbk(W+05-d2;SN*?04d{h8EIFS5pK2*K=?agoUs6k2{e0cKu@CkAX;v=j)(?3=E69TH=ZXoMGz6$VbhXO>{83BHxW7U*wMq7lAONwtR>%n|6'
    'g9lf$44*wY0^a_!_;-t+yKZL3Y38BZ%$9Cu+igZ^0G)P#m%wqFrj+BnZfw_S?19_Zwr*_4ZA_^d3mf~aru5m->+YN1U$Zy9bmAT}I^1g>hkMW7uxieRFH6#3'
    'Pq!VVK&Q%Rea{D5-9gp|mVJUzOcksKpAn3+{x!>PW^nr`WiUQs%Z;TY&Sz%8VssnWie#!hs7a=-fZ%pZu}aV@^tBiMhN72rq!6a7RHsz&3PmXz?DP!o-Yd${'
    'fD%l3dIs(Q+%69`F<;kei5Qf!8Nc;LeRhSXMMm6(vxR<8G;%96;qc>>bcApbE@r)mW-8)OFya7xK`+ow0+S8%ae*&qy&Im8NC{*nBtg1^3YFX_-0mCKVt)da'
    'w#AvU7_KR-#VZ_pW1jax#Jd`0HFg*yOcL<`qePfpjIpqW{~PJNdSeNRq9BX&;XGR0PBU32%qldFvR?n3+{_-Qx*kmUiPMFi5m9drgU$xBVdwqch|>`1J0Z3L'
    'H(<{7&Vh@d&8-)PC=85{h(ft)-yR+MGC-|uA+P9WzTNO(|7!zIt*t((d!Iz#$pcN6g9yu*++jfRk5??U3=%vvgb}cbxjt)L%aqKTb&jCW(@>JJfhk07GG(#;'
    'LlRLq&3s`k*vsDR9Y*OAUd;qk8DM0w3TT4|fAHsjw2;LZ&Ip}%mR)D#D?+HbniF?J(uf#u<@i(S`PFnvD|$8Ob+1jXW^gt@I!31gK2oA7tqU%E@NL;@a}Q;;'
    'X@{pW@#@->cRZ}_<cx?aUN<epDky^9;wxR5<67$4{mkHul9r}-8wdolos^e^5@{O&y;Q7pF26-~>t(peZr93jfyGUh3z1jWNNbVZn#2~qijV3IYa3P4i|jU-'
    '_TpQ!!n{48li4hiP}6K?lEmtAAS%*4#N1#_Sxaz~_+6JG6%sZRxkwaNK$f4JMpD^0YT|%ZjkL)~FmiI3x`)<s@&yW@_hE^b3J`%STIm28hA)#c&s_L7Y8u3g'
    'H!jH-pygzl>9(284ilx&8;?p!W_Phl;gn0C#OfC3^pWZjf0%bTL?ZzfwuY;dG_VumvQ}(sg=<9df`Q1-=v-7oUVB=#>F=DSiz8FNbPe?Ek`dFJae5Y>>u;mi'
    'B0|o!bQ$$Vv#d9`CEPGLuV?6`%(pMx4SP`!cKQX}ul4y5{?nTYxt(2&xsEyVW?0eYU7Z8y1KX}G4W*oQMt%yu1gTvbn~w_hw>kPs6Z+uM1Ah|l6_!vHH~s~A'
    'Tes_Cu)6OyD$5Y)0mmqHIJRJNA?M9nqDjLVY;79;wo^@u?b3S5aD%H*ovzCnDa$6+g4WG=31aZlgRwAyplcDRFF7nFE`G8lSHRiQ4e9(eUI+B^a3_H8nRiv;'
    'gwI~ry5QV_B!PP6RAx6mHyfOD#r3U1i7@*I4F;3Ue^AsMBs8?aD-ery!7I2LemU=oPlIf#hcG7G%PcTT(NmyiB3<EWUM^@dgREEu5VyRqO9VE>L9;FiIc5c$'
    '1f0rw?Pj<*@4~D&3=vt&Ip>!60Tw3cGS-hoG0U`QiIIi_vWQ+PSJGgcbH)g!sFJtmRJ&NzC~kZkEge)5{m8lC!x#wV&CK+MJ9XbnQ~B>UQg;t~+uYsI_Des~'
    '1gC|!TX8P3MGdGkF8BBvIhkNCGC00!odV}qd0&{ipq$;UkoSp40$K7X3U4Nn=Sv4+44}MAHd3y*5MGI!eOwsRVJ%lP=a=X0Nwx23Kd5(I^a;U3K!JU+raImH'
    'hNfcZ!mAJxZj7gR&3uB3UAG&72Y3Q&#rvsVvY!gpjSiC4h^x@i^DCWHvO1|!J4p7NS+SK}S${alY$OU>gw~Q=v1^yi@zt%5I$q{EUv!_#T`p2<$8pTWCUU-*'
    '3cI3R;eiauWMllUOHnOU7^ATQ7%X@(1jGd`h5#}0;;<P2hJUOM7eq?<LLtuLB;9PImR_~(Dphe(D)SG+X{$eh+lKbtyb>PThvi7pxD+ynAG*ko%iZ?@fo|l+'
    'x@O?_>7r$;Y7+UtC~I&pP{mV;X%&qHWeT9^V%w0S6acxQ3T{><scgQVz%5ewZr=KCP>H^SbC^V;VVH=1K|tf6k2)kp-O>W93xlznb)W<$EgW5Y!X7S;naA^~'
    'VsltZ#dCYw230QDW$${!v3!oDJLDiZQSr!=4_)$UaY{TE)e#%5zNeAUHwkhRvCU2(aX^XIsG6t>O*QIhR*DVJ)bGvDHIINhQpf@H|JDvv#dK-dan%)VEu$l@'
    'I*mW5MkEUjRQ`U@w>9-_Bie1W+~E9+$snU;#*VJM@4uV>f3g$sGfBZL6X6=rmsIp2%cfElqXRgURO}Olq!jut5oSD$0(Bq0TtV5lL<P45ut&5Cs)Xl2?8N@N'
    'QUBWc#|iU~*SsxO-AVHd_-@&z#!IT%Fs7$gwAC=?Co~$mCMYc3&`}Ak=wZVWEwr?nbMN?4VN_XY-Mf73Vn`dg)AK<%gU$^I36&R^zS(RfG;gGcwQu)0kRy(|'
    'L0c~Lk~~h3)y5ET-B`{o57wxjnoquWTJ=0J{DY&7b-v$*aaJyxTkW(glPf;UC*lohyEFUD>$eeYA?)aw{0p+)Y&6Vf3Zs(jHKGc_U93RnwXdc^(89pgsP^=v'
    'z8ih}AP%?=Enh|SODfndLH8=2?Ms+ugFMG(eKx|g?Oj>PcN>k*>^m;Yop<?Sr%%5NCk0+~b_evaTiQa<{m8D0yf+;)fN_ko#caEg*xN09OoQj|#lfrGXjJns'
    'VIqv)OrYu6{W_}?5K<q6<Akbr)$-CHgMJtX^^RwOz^#Wx{Q>0EYacn)tw9r^mc10hIhXL;PWz*q$`>0m)A#(v(=KtEUi+%|+z3UBb7AF1@#Tjfo3Ol&Rln%y'
    'i-U4P8SbAbr)MfsMqKl~mRb{{gL+}<=~l}po2w5ZFqhoXz)>JfSB99VbhP&*E@x6;V9V|PlIb!{=cb6Pe@mB@KNbhYdz&EYHXVx8K^mY=(%@qi{yvuqN*wI}'
    '|NN{Lo1So`TLILA=#GH_cE~V}l1eU_7sn~Z|0)p2tJX!uTjV2nRS6x#OTlbb&)i@DH~P*F_g^8~tF!-#y&VG}0>nb*jbOIUaMesj>jd5Vib?iN5$|4WlALI*'
    'e3svsogJ`$o*xcZ_&6AnSj<7L#7VB@C~R0ahwV^8(>*&4?-%<F7suf9WKwrJ>tzT~tJWwvfAusp(%kv8yuIl3S>Kd+_d22+MU2cYYMw*MT1p=j7A;?Y+$~J^'
    'QGG4sPhSnKwXgEEt@4)q>=v?Y>r@c_XysQyD0Q3ZcZX55JenWA(NL)-x__@;oFea1B-_4G>gfrB_OP_XIpdOly+CJE``VGt>)<V}is87>>VZ;Z#yfy9>PidH'
    '7#U<9?K)b!+G0RF1en3S)S@Pn6%)wm<!n*L71>kLf`)!<tcUz)oqy$yV{2|w^dDsfq5e~GE@^{*+c$RFSZy>erBOApQ)$|WR|1tRMu5Z=l<-pG)aPuA3#_6%'
    'Z$sgZx`_+Ikt}0gyfUukYH@7BjxcrcgE>5UYL1hWTZ!lg_QX-;hw3s03m?bMtFo+D`mpyW)7#AfP!{|n91`Ly_ez>A3lGUDtnV5iVk-I%XA3xbd-C?+wTcnp'
    '*bo&d!Z9Lla0oe$QaK$Ua;LNblN(ge6oiOG$Jyo8aF)#_f~9vlxz4^uGJz8vH?p(CzbR~lqe$SF8#MwC0zo72)D93Kxwe|b{D$0?kAHiCUh~!Q<YGAbP?ehQ'
    'IfuZBmqXyh$ssV$`R2nT<C+gYJkNZ1aypxQ$j0WkA?|_90dptSz`Q7r!2EBF7i%u&)837xTS_7)K>N=H++Pk5UJ4Ap6cD@!2wbN1?y%qPl%n|OT5mqE?nuq*'
    'e=vi>J?1pX$b~4Fw!ok&5~+omm=60NuBLN|9hh7B@@&B-mlPo**PG^AX%OcBv(q3TdPy1u5dKTEC7i61E#YLHYza=1g#UPM1Pk-i)iH;{xM@$?xeyo>CWz*d'
    'hqkbqvN165aZ{m=z74f2XTWQC8Qul7DzQs<=$}#QuFyR?ndQ@RP8<>I-M%O{L}AtmY9SXY;b&+lxw)k3{y8v^m{A_dpO70XHK)J<8#Evuy?dMBD-oTj8vjUB'
    '6U+AzeM`wV@nz09%+-*}#JAvBS~suozEf5%Fyk;HzBHdIyw{a%EIUyDq%qrB5>Bsf5yg7M?x6&!ocFXMW7%qOU5<MzX>9eK<9WqiUiAjB0~U(VR$jf;mlh@_'
    '(gkoWFRArQw)4EAu%r`;Mmj+=4}qJ?x~cj*?N+l>%G2a_1W$D<WIbD3%f?O{MJ6X}XfPatM@Gs>9c3WolM3o*Yn8Y3@}v9GIZlKQ##4HFwdm^fwA@kX!Hc6O'
    'zarQ<E~~xV_>b-g4Bwgbyz@Ur`*^9<@kg%h0Hv|EE85ysK*lKvYc<?g{r=UI0!k37gPiuV{^SB$iO}zi99l76k+r=9?2vPxoy>?oU7W(2o-!-Lf5QTwvhx`p'
    '4LawiI5W8Hq|rQu>0N{~6;Qq9Bl6BZHOcs4lUcjo^lx*R`?flz9o^lIzt1?rMur58(GdQ*lu@alM8^1p6MsRft|5<U>WxVu>2S4S^^7|j(@d&9bBDu2Q6#3L'
    '`pIK)-_hAu@AHYCr8HBg4ka)fx>KU#_QpcHo!axR`<Ikf^y8v-SvqB^OGJyaTbEW}Vm^j(@l?@PmfASSVQ(~_$Xv~V5}~$X3PcbU4`yFS^XX`~a0C$?k4hYL'
    '@--6&o&4qW(@KYMpXzB<XMuLQTqRAn<aj*=bw#T!RE>^?+S6X&Sz)d9D@tE&saQxyP5Kq}m#wVUnicuMU06|NEqWIDbUjV=y{L)TK{>sn2jcx8lztnD!kW2D'
    'R87uvdgYMqE@1bw+2xh&f9r54{~>$e8g@ZP=CM=``(^c(+XaKZHQGMt?N~Q5fDjIq=GOA{C*`fr!{2X20}5{%c#V<19!EaJCIx;8AletFSI$@6oqWiF((7Cm'
    'mclu(EZ@SRhBG?rpDShjR%7cy<56?_hvUPO-(I{q*}NFE2nH<Lc}O0FbK^-l8INwGX>T|n4iEt}vUl&OOQDu9L`(S62({jf9zsuR8_i^EcPF~Ypbl#65w{iZ'
    'N!8XDL*#1bi_L&OWYVQ#DSLl{xHMP3XBy)t$${=9K57nAmbpfJ!IcXqZSeH@upd~VUj#n*ZPeV6NmM+uJu>q4($8;uh@rBW%(7O5^V8U-`6)QFdLO7sz{+g&'
    'A#HV3Lt4v`BV4~V#R9RExBy8jOeKa);F(ksi?meWbr%i?3g5$R$H>94GEn*KYLq$d{yBo?g(R)l{)ghEBUXHk(`I2zO%nO0)m&H&;eJ>_HOBT7e_lE{_Y_^@'
    '&{r$c#`L8i&?Xdvexm|waAe_2(GHx!4<3uQ)DB2-Lua(%jw5H_BaWLXQgpJu#<m{h&BL%d*g#wy^oX@sLU~E-qq(&cz5tQQRS_|XNFYTYm+ttID48!yHM0zP'
    'z4XdlA#|O~dm%w9PC==Y?}{mDN@sOE!6hlAB1@_-tvVNt6m)!`DYbTrrk?Of#2ugelud0u3Om%^FYtT7FoPyNV`xbt&rlOYrf{t_R%Zfwb27*<l&zaYI%c)L'
    'mqa>5#1KPBY-y<L2ofQMGvsKDT7|@bh7j<%r<J2Vr@r<Hp@>R0sFU~2a{KSByr=KunAjVx@J{rnOY4S;=j$E~J;4dn;RxnT>5WZ>pH?USFPKPC%H4Gy3k_2F'
    'ZK?Ht>ugIEiEyV$4o6wAty7sf6HEGx|6&U!1iOG72YRJz%lGL|&n5P)%Aa=Ln_a^lOgMN-Wy)4Ox`HsF76^nFQI7<}TM#G_B#~sqa~qLEW<wMUtza%-Ct}vx'
    'Gr2I?|AtFT>{F{>L|?2dGDq+01n4Xe)G74LEQpm|J!GdSbZ5L0i&gSPdC<)rLTyYw&7e{L{zGL-@>8xEHRC0$3<S=s5J0oODDjoER+hxkl*H4lcnho^U$Z>U'
    'Mo)iXsLhI<Dha(=BLt`5ESW@^-Zx9`s4u|a_p}ywPD**QmWMTaSs(uM_0~h!l!M-syi4Jvx1#<C<oWu$9%3fXdn1IB&Fa|&b(}Spm`Jj|7+z#>f%LN|Lo8t9'
    '2z@jgz8j8vqv#?-_}St70==RS&M%<8pD@@sI{J4utIid@*^FLb+Y6}k6pzO&L)+dwswwqtb9XmJ)!7Z!PAEikn9;0%ML=yjI(~X}IvVyPa$^<vMe;M4c*W#8'
    'K1Bdjyy?l|8>^<*lq8eP{F~9+bG)PQO9o~f&P8WMXws?!h@XqiCDA{2wqaPu+YiL2wvLaf)0w86jP6L&cs`j8{|!$b?va~=-3<H~o3>QO-yYAm8iDEgbq1S&'
    '{dN6e-T?1{V?x#j2*-rFOTeHvG`brY@=)Y!<adB8s>w{M9sF&i12F_pI6BR4CwNgJ_HZ9=`77QYd#L|rJmMavl;RDvM~|pYzG`NZc?Nuf9x*mSIo#E1@G8(%'
    '3_sL7$v#7X%?TQ0$h?kqpju9F65hesVHb9ffj1Y6b1D{We)jC>`1!w%UUi?mIC^!MKJ*_So;*2taq#BwX^OEe?z@-IkB^UztrySV9KJkBYgGpJs3uj$^ngDM'
    'oCo|MAP@NO;V-}7ujem*h5sO!F=bSsno!Yxl76bPrn%axNnyedsm4jwX!-G_)S;Wx#Vq}_Uy0KxC~DN_SdzM<q4xFvs;)f&OS(go!RT%ZfIk*gvjUGD8$`Gg'
    'DCNTTQ?I1wr4vj60X&OndQU&;-%JowBH4Iyx<uMIJ4@O~=#gwL_aWL~y7-rVVrZOsWX#dr9Bh+cpv{v*;7!x+Z2Li%&wZvnw&^>~8h5kHtKNu=!t;dv85FM#'
    '2PUDTk<!~XzwIRat67)du1`6#88_p0m0163Cw|Onlk8_{O10|WrT_~TRtfdM?L5t(qcaBfdXd@Trt{P`ms35^(jIp?^}REy{Jd%boGFKLJ#2eO4!jby4DUen'
    'scIQ|g*ndqMLIRbj~}$$s`2`4#JS1#zDjpkY6Rvt{3ZaotNH22>E@$dcdC)NvYO7x;sDoMsv<qaK>giLnl?N@WJzC;%j=*(n&zoRdDsO8N+!7!kan^!`mTlO'
    '_!RY>DtLT~p>D(*CKUpejMLQ1<)Hez73i?eC}v1&NmI=b%D$O9Jix`f6thAA=ksX0MVbw`3A3?v{~{9@zH5;cx*krh7{J-wpp;M$Zcez`;ak4h`jd-`2?x+9'
    'XHYbkFiSPT#1F&;47p{v-!r(UfPKKba+LK3KiEve&2T)J+(flqW=&$PpO|~~oJ~ff3F0Yon{Z3g2Q6!Oik*`@0U!rStJJgJIkb)ayP6w-e;js7Q%H+Y#oyI<'
    '5C79;zSMs!kE>?k@u}@mWtGy9a<ZJ{%47mm@-zdV!ogaDrr;Ofq}ZnVdZVfQx@0@%8wa+>rDe<!Re>OBjtD6mmgB0O$AlRqFZf5bqcXAFj8pHF*PDrS4^OP_'
    'JNZ9-3L$`56Ug%}y-V6YXpcd2c$~V(RcTs9`K;=qfqAD8yU<oIJ89F7VoQTDY;EU$DmvY!kDRJL<rIB52bjMT2(N~Lmt*fzZvJXNZA4ZBba+)ZzPbJJe%fs1'
    'af<ks6^MI*46aj0%<m0cB)cl78&m`IB2YQO7qg<FmUB5{Fyyo(Oz&~(2kBMmeYMkR`(DFJN*v$TSl^(RI=9TQifKyorPUbRm)tgrZJlXGQpQDgaf;|<l14`8'
    'me3-hk_z&AK*T4Z96QuI#5TK)YD8#|#*umwU0Bg$3B@R+Rb0w$xrUV@kgP38#Vz*H=`r0pyP9D*t)X9vxFK<2V(zROPLx@iP)HaYNR_4(e{SreDm1^wE7i5J'
    '>(+$|{a8^Pqg{7NkbR-e$Gs^K28YhMh__)%<<v`za4AJiGy!9-Szxtox)vuw*qj22zQxR}r0mCNw}5A;%I?@z*ZqsPT7qXjEmAhBxiCyMg*}QQrlmtstn0wK'
    '2KLTVOG03EAiYbJM_N_nfT}*-u&(EiDXWXfe<${LTlQ(5_drTdi^|4(&KpG=({mU8NY*GXO4tLnSSD1ljBfLpMX59TMs+)djI0cR+_VEIJK?@krOsYj*3Tku'
    '@nUCj;viBJ3E=vHFTLvbN;kGAH56<I-vb=+Mm;C+{ZyEHt~lof?p3a5@DqQ~0;<AtL95+K^sZ|)lIjQu?5Nrbs3{U=xLV{F?yy(%=(E>rm<G6wY!O&_ZGTlE'
    '*b~cmep39;o|1=Tw4JnJlXucWK8!AgSXYFK#}-m-VpeZ3GK%pLRr-`nP#O3}LGf-*IQXKH%LYaXMg{8zoLJmK5d$8!*KiuudIYDTuQS@O@gDrQhlZm_UUP*b'
    '(RV_*8%*hqx6kRVQICq25xNW|2ff?Pz`FQ&LV4h`C1SL#70`MBp!WzO3a^o|^kipw6|(!#s_?$+q#<P&MXK~p=QYN?rN-kr|A40Ac)zi^%ffBo>&I>j0t?_i'
    '3>c2BjSCD9?lRsQ&__Jp%ev!JHDC80sGoN+$OLKA*~jBSZ#GEXOzsvv00Qi0Y9~_iA-M+0_nHHT5^^tW*Qyi)cryHVR!y3XIH^_Xti8@=PkXo31o#1XWG9Bl'
    'VpQ&;_wglNvPT363tzl}FR7MJj$ToRX+5@@5BBNs?LT<*K-3Q_C~!&^!J-@9Oxg5OFYJDSV%6$Pxs<-7JBB<_Z}v)evu=GawEBju1qPO*U2a363LSE4Re7ha'
    's5rmEo6)|hoEXWi=I(ysg^1gtrRy$XGQXhfq8hN3@x{DAyz1DLa*pmqSPtp*p7mH=kDb(jH>h&XG<o3ncN%5rq6Iq8TP$WZd+1438|<pccg8{Uo@d%i?b_vS'
    'T4va*R4PB?^>#HQE8x2s!rF^m#`h*!TB7*~rY!1RPlkvEaRZ&6!Oc19!F_p-q8Q3Ei#c3j+MGA<on?z#g8GGtSj<CKy@W3F-G`gh5mbyfw|>moVelDoM<=4J'
    '#|NUUXV4gC_VMu<`cBLP%syo&6bR3>`})Pft5=7|UEo=(LaAs!R68sR$o1KF<bqDZKe-akC8FjI_06g6d872<>`_xi&zou|`QG-q5iPYBoyBQ<92HKVV!ox7'
    'ysD-jKW?($8jJ2Ywl~!lSJdv45{7?Jv-rSLiJr1(m42EsgiS(mt5RN^+bPuOv5Xr?0!D3!Y&K0AcE(D^i|)Hv(W>hL7OkqWGW@|@hLlj@k;xNQJW2Nhg0{QH'
    'J<L-{J~jHV*X%8kNYCM(Ote5KwC{%>wszpkr5n~cgmwk)HpGL`#e)&pi585cYT>)Boo~{u?N%VH@P2of#EhW^q92&q+-{3QT>^>vYP3j$z;b(R@g1a=Ui91O'
    'IJ=l!Bf~q(*kuU*xV$1)x_%F#5NH{R=wxFcAE?;wEhZPke$+?PE*al9O>NM<DVpuCV9`gSX@ZUd?J`v(LXYHDB;`BDPASTT)oup!Nz%qs!{2ZKerUbBX^ztH'
    'gv5Ijp?zry4GBbmrfv11F{35ln`dIp>g=JJJGH|ummaye6$A_D<F3G^|3;IGaK=M)N=x(D0jR{nX7^p+zo6&eZR&%%?@_Jf$yX&$zG~2uPvtK1o$>-<pH<8('
    'RE=E{Vcz0m<69yc?kl>tI2II3gpR)Vh3ug2VnW}<EnF34PNV_m!6&gu%X6&KYe)1J3urpY)0C=%ZKJ8+MzgH1`jZBTdh$})ZuPrntD}#l>zZp{rNE*pqSfWw'
    'yep0%$h_b}<4->+7dA;g{ainDNXGZbP(<Lf&W0Zmc>|^i4-H7-u;UiDnk;HnqF#ic{iH2s{*KN@{L=)EwwMxxT|s6IiM=TOqijgpUYwF4uqnWT&|@@XQL*=l'
    'sth=j3rxrIzTTwQxcKz<bPAOMi*$325Cc=4z4g3z4dQz?9c2shnURie=JLPi^UNuS1^rRIw)H(UCf<+l4N+?9=>m!r`!hS7C<C!vHLhf2Yr2YzVId<J?%d|i'
    'j+P5|Lze;P9Z3U*B_|(_ZC0Acj~|gdj37Sb+=$_O?W&dcL_3Lek~Z5S^aIN?RB8)#YYlVLGP??C;G1Q}6)w^7FKpXNQgC70MV4OJI8`Z91&Y@&GqU2fEmd`A'
    'kACc)UJWQG3GA4XNpyMU0{(h$JbZV)NVR2jYuiR*Ol!5B1ho~r^zWTym;T<3VFQ}`j{`ROMo_dZPQJhBO>6Wj;aAG7!<rjxyJgixt#yK_ue@!OzZoaC0Sv*w'
    's;wNnmj%LTg>g<><`&%S1BnC1I8Gci#%ZkmxW~Xhr^e}-@YNi2wfM0{R%51oGUp5a-@~Z|E2dXlA%ba4N@48^_KOB{1fDCwKwRQ!9%<r4FASfKY9`pMvQPGy'
    'q9&sWEG~UD$VNltz}R_OGt{&+vCc(1TYx;5@`!N)>Rb<ReW8PPel>}Irq3dFP@%sc0~cP$$@BWRdEFZU+gFR@Fc&>vqy-m|s#)d7qoa{3plSA@N;!S~8L!6~'
    '?IMfE19Hlr8LrRQr`A*KL*Yr}|CAlZDcru3IqaNvm{RI-09|oebE&jrFFR?+yDKlgYCPVf59RZ<_5kvX_?5Tf`?wj@ZD4xE=JSmvmSAM0VRESg$92%P`tI^E'
    'c0~)MBFR#D(^LIbXm*u0h-0j}qz3^WimkEDB-C?%<G9R}x|O-AF0TQr9!m>S*awzVwdYN;a>t7uS1-+7jA$at*?N~XRc>EsXxmdJFr(!88U{8~d%(i>+1F*8'
    '<xvW{BGx!<B*BHwKUX07-eZB`3Dra!;H)<qIiD$gTF8_pyH}j6NZIFZXy1&B_XZb`AZoNZ$rHE+16QQ8#7YsSX|Q`h9_y-_omT0l*Ry~dUwyRI3EG=WsxdQ`'
    'x6ODq#{VX}O~UNsGwA0NxI<pTiG}Ay=A4!~(>dWlpXz{)O1~3bhDZ>FdhXyVczct~D%M#NZ@+@VmQFHs0*#8?kg9SOIgccyA~&_Kq9SKp{pfmUhmE)Iu5gw`'
    '&;(JC^xs>}WNQm#Ls6aMv-;LHnsw_Lovg_W85#OEsvZ9Gb-lT}6Gu0btI;4DTwP2fm3!dLxhlp^QdS@YS&uP$_#m72LB{QKVCe<}`3-2D5K!mQBh#<#&FDnp'
    'K^9~jA59SI3jqNcnp*Nl!g}8l2dS;$=z&wWqBW##@hw%sG9UqqjNPNpD2Rov@fcX~`j_srqmwsjn-2;d6LR)3Gp-po(j&lO!!(t(>$t-pj@{p(hTo1)(i+Th'
    'w6zt}BNa=*5e1PGArPq$ib&!VA{7Y0-y%55(}UlUK;W-~<6oY?O6w1}x5}=7h9O!8G0UOLg?_}BwDU-IajRhr61QFTHlPI#3gy1rvjQqobD%CgR7>rfk*LQY'
    'qdt02BBYnY#d&gj9G2YEX5-GHqRoJI*AY5YPF>pOp6E0dZOLix9lN=P%nMXv%n9b-nH^{3v0Sy+QZ3{CP*|w`OdYuTqepeUgA8j=)$ON^Fc(kGaGrWgxx?*I'
    '7-8BDc)|+gkZ}Dcw)8n%wAcmJ_F+X~$^oax1hA<YpO+sFOYdDSZc|E{OCw0=6Ax*0aT|7BMWcrD*_G3&vEcH)wXlu0S~ONAS1T<K6@XUk%Z<BJPvNnvS=AHm'
    'qEX|a;gC<5KWp!9;NSEjejMJ#h5)qv^Us`n=)K|CVFOXjtv+7d*fI{DySJeVTU>k>FCB-9tiaPNGrEx8HTn7fS~r%K8h62jIW#EG(S%kuXS)v>-`zE``3zlU'
    'j*n1Lvjo0PPGTx(5fT4pLwG7lc=FzTQ5rqURhNCl<P&H_qe~r;qUyl^OyTy<B0O1q1rVdJebolpf{k(18P(!Hc6NTJje}SccfYl%n&ZQx<EMwm-CsEOj@Sg%'
    'J4wJpCxRw%mQgRYUt#1t#eS!hB%B^w^3U*M3e*t^(2TMvApi$2%g_Y+$TFecos&3ft$Pwpd$Zof+z7?&vYOM^7k%foK@Ta@sB$!>CkSl!p(VqO<)HA~k{2z<'
    'F(PYw@bW|{D=gdk2W)TAr>rNgeMC5GYNe`?GxJ!}2$@57B=^Tdyr9Yz+^v*pf9NO%oL;-MjLW#AS9?&1ZucTfg#GA(#7wi-Nccjfcl;N<a#x{JsT@;iw`&%j'
    'X0tjvqeMT@pJct!`yQu>b~_HuQj)3c=rvNt!AGS1%LcJnX^t}vC8*6ZSlg?NdZzw{zQrcC3Hq=0EDj~!(|8zd@t5b3#YtrS#yUECSS1#uO$`5%YyR>oyUI-3'
    '8$EG|tztc(IxNP(LS%tk9q%@-h*4Fn-w5m#J2@E;q`1u>()e%BqD+B+oLwug0Z_SNr0!`aWc8gu{klMV7=~zJb$bvr58D@pAaazQvBA&N`?vu70k1W}Skd?w'
    'MR{4htAIXg6rxCt3FiYR5ynRFxrD(qAq1weHB=VjoT@ki5N)ttr@3q}3pc-d9PKt5&};ymgQT!Q;fgL_RoWBqJr60kRx_Icpd7vX2>l&}y#~}rg000XS+Gpp'
    'd!9<Y<};d1n`HA7jIpAqGEFSv0w87;n5NZHQT6A;<2TP=Jpb3>aW!74Gme&hd7n6kSXsXcflBmd3c6ZIukc*Vjk~5iZR)4N&A}FL-XE4r&gvWEl8&-WOK_Pl'
    'O$Um%!(^&*C$km-Dh(5b>CzoTJRcBM=#P`%nzv*z5{xs+dnJ9<LMjn2N*rH@lS$+oYuHG65XESxG{nbIvlZ#6zyff!GMr(z3u(cqH>{r3rDuCqyY*nZJQ;Y9'
    'd1&@N3BtFL+mI^cY&ETJyCy=2|7~_$rr?Y`T9BE7TfFA;0shU;As&w&Vv3bM-2G@kMIjNrFG$E#0fU&djl;WCFvVapo*-5X^TPt?y%=V5?L78Im7>fyBOPXa'
    '-XpiL-u(QBz6c`(RkA?M@?wve4QgE20$`s8gH5HFz;32GqaqBjtNUm@XET-w$u<63c(=QZ8W++xWH7n<3OA({qZ_;}X-KIq=RwiI5NSs^1KONt3s~CT)ky8a'
    'cDrM|=%B2B)p9)ygh(wZSJ$&hwnQH~>x9VJvxkjfMhZtC;&kb=hYb*%W510*ccPt9*;A;##C(IXhIUj#pd&>b4E;i6G;4AflSOZYEXHOdkB*S&_DFxE+s?}c'
    '7S1bw$o?4W6aO+J(T{TNKmiv1os2Xxv0O~u4f)x)0EQm97JKvH8U=0{wWw1`tD}0>qDll|(_As*Kovk8hO>EYFB?+2Y!j1eC5bR&k|*h49};OGQQH;i8&lxV'
    't0oUupL(h}%we09y<4+-k?go{fkCR}?Eyn`8UP^1RVU<AC_`mEmr>f28@YEXLoB{_E)FIE?u8*Tzn!bp4PVxYHkZ1b892JFR#d1Px09*3xke^QRKquNDq;ys'
    '%O%a|SpM{!)(>uB!~QetucRmC=V7L2qG;pXk(Y8=3WKcCdlYlrN8H|fw>?9u=I!?#_m^8gd>NERwvfwu4?AOse>`Z(cx}4%-lrEh3-9ej=)m&8LsP%77hF|v'
    'kucbsI9L<zZCewH(J1jluOupAEXYTt=vTTJK4Gr<MJsS}8Xm0_Xh_XmrBh?EFRRxKP@P~>A6}!5-v4l1bYE6vtz>f|C_<_(UFFfG5*6TE{?XNk!U!bT8(v-='
    'cVXXgr<80&?cmmX*!|c^+A4N>u8e@!O}a}hg=90f9*Ev<6CYf0!t{BK^&I0kd~5M_Rf8@dPur9mQ+{eNQO?c`wdSuX0g}ev6$vr;jxuHD@47zcq?EC@hLot7'
    'TX!4A7wWvVygTaJtP3$J`Rfz}3R<WQxbAmbYSFI!6~nJR+!OP<I0b|L-YQ<a8KhdI0ko&2Pa%_vrR;52^J?BIOGbNT1>cb~7M7z%>(r)(xAIUn_wboHZ+c-0'
    '5um6kjsbf|ytt*fC0`*c<F)11<R`;+ZMdA@EsPq#3R=t7>p@DOR3|zn5AZ`}n8JMQ5~j<@Vp0PF1rQ%e9IOp6rqRXdMLt1m0Bnqk63kc;)`-Ifb?=z!Pum;T'
    'PW2be-^VjSYeCq(xuAMNe{b^S)yNGqZ>m5xFt9BQ!bqzCl03(~__<Qz<p{6&bD-={#VD_Vm2mN1txDN=l*0emrv*V(>b)C~f1~qkHi&L!c$ovS=Q|w)Km(;9'
    'P@hm+bT&k&&hrUHT45_7Hls89fa6AEYC+sLzSIHa$<M!}pQ@Mz3NCka+M_c8f*3w}mu2(JJR0<F=kTlcFo~K?yjjIMM92(i7(&;h=`GbOG91+X<mhd+rSK_F'
    'o*f>(hM(*`Ql-qe@Dt%NKht+7Z;tKHB!h+ZrFo)0#(Wg=^%I;A`F5w#&|mH1-%@_N(U7JN51&F|)?&7r4UKNu+G=QkOZe2mxP)>I1ti*fsA{r8Xn!|;E(l~V'
    'zAVH32mS-|8_-{Zcu#+yPA2k~_H{|BnDmzZ7-W3}cN%yeFyrioBWr7(b?p;{8!^C%c>FQO2_rFATc18BRl;VMKYOE$|H3A_*lVw;1>Bw}iw?&FMiol>XYW+2'
    'xKUCY#8iVF%7J|MF0Cm%RsD`gb<KfEHSdHS8;(AZ<)4#(*~qJj4~Oa_oBAoijQ<Y~0#UeVW3V^>**hj};|ZUESSPxn>}dD{`|>!|B|$Ew{AB1_r@S3#*ZIxh'
    'Gq(|Q)VLY^t*hW(`IYd-_4~?))ASYQ*{g?gO5+GftP1uoRJA$zOM2*}4Az_FY<ODJB4sZ*O`AzG7!C@B@bziZ+c<SeuT>kW4ejtNkvXl<b2lV3&rWFkzaq~d'
    'lxk8p{#<!Unahz1d6Lj46;ab#8bB-oHm$-i;zacfPU`2xk;aNHwrOuZS6b5fdCK4`9L^(=5%C^HXEZh&d*{O$Oaac0&cj}%XA*6RzWvY<<@1a=z~`yLfAz4!'
    'blP^p3v&`%6vOe0BsvLrI8CPM#K|8*)(QtIPb2BId;wv8z5xS#_&s`886PapbinRd3c7H@;rVg=Jx`V8Jf&XQqO|ISNipVk1t)hS)y;h`7m%rOx6vr9QYkr?'
    ')LAR+>qfJ<a=hAB=q(mAbv8?S`{Ll$)2dWagMy7@3;zXoY$I;t)Nds``LuB`&axA#ibKD+8X*<531i-$zBdrAZk>aB3_(EW=E-Q3&2mwh_N^3-%!HkuDlgAH'
    'OdDJnq?xBIlx28NIbyo>Vo%6}<6^mI`AMpGe3EPj%0!<X3$G8m#6=0L&q>)D!t8U-AO(KALEw91I?MD6hypa8&C)T<g0kH-H+9-#WFBbxs&k!+$He5;rsucw'
    'VINUQ(0dx?M``vQVFWnv8jO4F#Q!*PB#TKpMLfc)d-fL-<(<oQw)j8o#iV1qS*mlrnBZ}!Lrv^1?SRa^n=Huj65d`efFvfSu6WP<T~DE)(+T+fxRKY1q*&A0'
    'Y;plrEhe$Tx)Iij^H!zaL#4<^KYXVdmEcvey=`50=bO|#h5jk19mAn@HcXfODb{YTDqw*b^BkmvgIdXDi<Q1A2wvTwshwBj+h}W3?~?j-0t*D<@#%aqTwIX='
    'cX}JCeajm?s`2SQ&+wVy&)^KVS<*ng>3#}-?x*&{W+xPR8chG9Q@(f*tUgIsUN1tx=~;8%(8_&_^Xq-Qth%6+)^0YuGEr2+D+ev|u+J^u5BNOAuUf_C^Tlk~'
    '8;P&^M_-%%F~R4eL;uJ*!*e=x-}FPLjH)em39wNjqz%GtfbO;y2w}UJg!2|#+#7G6gj$OCt=UAi9J{6#rLi;;yB37VW4L&l{Ntch=%4s-wP<aS?6iP%5LsyH'
    'rA`zPX$5FZ$fjfUkLA6Nb;<5c?D_dN+TM(ACa@ec6;B?i9C1;NV~L|5B1&fm|25ebdBR0vl$2>=`=Hw9Y1=-%1rhOfkzho;73}Q>j3?haQQ}gZ{oX%)aA)cR'
    'P82KYts^Cu0;+mbQc>?s`u(dZ#T*!owE<nhak(~T8L1#0X<!r|+z2lY`WT}U2xCldUVO~^H{@kMzD})cS%5-ZI2P-@9J5cBdAt~pg|1!3VcA2uJB71)3o|fH'
    'u}eYDR|3m53x@^KwV$(h<5v#F^6x1W?xYll9>A^Hq+64olHy*7BiF2=;`3lMxX7DY`p3{isIWzk+xVzM(E|miQ31^mA*wOoQEw*vhe(&fS8=PbLX1j=m7qTL'
    'R7i5qnv9}v$;@&#yTE&!gZ_z-`j@qiWeyTG_&!Z>+$=NGY;cxxJyAp}c$&f_O;!fzLXLe<{p+OtI!-IkGchRm(;_ycQUY3ok3H`+!*3HQxsP3xcUF}ZP`jd0'
    'GU*Erh$01qQpqWGT){NMBz|M2SvAHp+XyBUEW<8xSgG=igScHy1)OzI^dNY26=SNXSG@8Pv%(F;2>35OS5=Vd3!lc$@{*#EF1o_iH5Wuxf{cA0F~`9Q!BO8T'
    'WvbmW=^fo5UrT`FbdOatA%?@35$5KKY=8L;w8HwS=}*(pBnGCQL&1%VV5+h*KN?*}T%6#tC};a@GDwYjyNwOBRX;l&z1XNy?X<D9mInBl&VY!*0JUV#y;2Ip'
    '^wYZnLn-YRmn+v-wU1S$?#)IgQGe<btlvgEn>x9w1a?WD73A3^;ugbBB{50%5hx~l1QG@_1`7b=GDeg*^x2EX*-hlc6*521E5J(b1Z@ei$HCKlNG4d1EX%AF'
    '5M};`1U&xJl?-K`{dEp4lFd}v3AO2QI55vjwdqATF3YpIBqId&C~u{fri%N*5su5|qOS67<{F^yi>qIrX>*<N=@3SmtH(v&#rW2+(;UdRSG<08E?}J~-gR)E'
    '_)W;UmSfqqf{8=VP;^6^-I|eszuze^&{9NwIiCLSHrNMNy$;j|S&l^8V5(x>SLzy_au^W&t%m`jjNrcF&I=wC1s)qDSFq%o1r8#H=Q4GE8~tPF#|U8#hNrBM'
    'Agj(~FgzRfISvzUEA%a|HGhmwph3>AvenpnfNT6MJi7(z^lPs-j()isql5H^-n(~jy?`Y5Lw_>Jewbs44^ZG8zW)JV&xU>2TvxNKzV&dcQJ?ogvZUG&?EnK3'
    '&qk9QCZ-gOlBnoKCKx*UN`)ByAf5~fU$UNgnK9TX^`{R9+=4CF8_&-$VGQP;{Kw7%b_L%~#G@O%uvLyN>L<A)LYoQJCuKzUS7)RrOpG<Tn)NXo%+(wnHM7|T'
    'Ary}%^~v;y3mD-Ax|W}zN^#m-oX-;;Jn2Fyi8tORb&UWhI>?@0p=qxV^9W_!gr?FgFBym1jo>c~$y~rek9wyQN}`%+?9xr0XLWmfhhmJd1oV1@pkAbk(xW$b'
    '8$z3+AB<qEYBeb0FC0Qe0+#UU?ujQqtD5W-i3(D(k#IlpFFVO0eel!4$zhtKSDKJzSO(EtdxEwV^7UK=T+mmd?>BdLRQR`8<My|Lz)#sbT>W|4?(7Xy*I9Gl'
    '`Z|wJEV*ok9etDNC;p9MUWh1Tmc{qvOotoIpeLu@87(VG#qV={cwf|q_n|(#58?B_uMaUyUrmtZ;+gmGOnv{(p{`M3xk)v_u>0j8gRsTmgdn&P?LE(k5$^%X'
    '55QZ9R&h^nP@};CQa)QG8Qt%ub7mBRw~1DfPoMXQwB?|8tv1?JUkmE<IsPf>OY@A95<E;pEow#0^EBQwui8^535wf6c)5}Ke4Q!$0q%)h*QeUA)a&jg@n%lt'
    'iK$yJgT`9R@vRsU*1|S@XoqQX*|8Q9Dz2xOPGXmf>Ec%6F_^L;ZOlGSfocvHquXfyVMvCaQ;rFq4k>{=hX$jgE8N$cc7?xY2ypWe2tJZy6%sNaYJ4>o`n4Ag'
    '*pf570uke<-+uoA?SD8)HyF=vU)Ln=;zmhvd>c;00DB9-c<Zzi>UcV_lw)JWz(iBaH)($F$W8@LFkcgHa;t1=Rb_#X+@w-%@T6H(9E50|0l~I#UP(XjmHfF3'
    '#bQj3);3*V2Z+v)@Q@=PY_og@&<}=+aj#p>5I*P=qu5@3A+5yuDxT24qE-Zyu-HInVl7T^FTeoO)xX<{GCB*VSGVX3=Un=HDllmfCbpg=oQ`xnvCN+&0L$&a'
    'OG&q$zdCr)eRA~j^}&-jsWYU%&{eFkZbzfCoP-|X)t*h^!RFzI?%}e@&d#zv;S1YHJp~>mz@yU*u*Z}&=lxMcTs16D>_qMh@#HkO%f78&+P)I1*I~?^4#)D6'
    'hFx3f!`G^=iC8B8cD0!&UDD&9^mB~e!X>sJAcLZSuPi2I7`CT*9Fxs0nbwWBuW9Ig2Y03YJI@)#9&4od0J2wn`W#>ftbw%Ncf#=dlVZEU#2P&6<{g#*UlK}F'
    'dqP<~e2zf9*hnW1dLnZGKEx95Aup;Do9o!nOE)x*!V3?WMEk1S)AyJ2Vox)Of2k{Kx4Rxzs&yeO`B0z(4NlKJ{ST|VZZ^f^dOQIs6i#Q4aVvf$QNKC|iM)rb'
    '&Z74r;|v(&Eu%cE70BPk1VbRP#&Pc=n*-g?HW3Qt6b%}~1sX(p(HTh3=g}WD+&@5~WyXu-U0}WNLm+vJ{<$;+r59MEBvieA1W!g8`{a-^V1i+R!vW!w-a=QY'
    '26C^6&{Hs*$D8*)W!--?o87}#Z;pTeB1ofReBEgIrqNv}k8;5O%X{x@>`Prs64}s~=yfIEVd<q<miM|Dx1)b-H6NY)`usJ)=U|}T{Oa91*a)Z|`L-Fis6a%%'
    'bFiZp6WA~l)LGw1=9WS4HbS2VtPlTgK1zV|Sx8CvNRo6!P#?X2$jKC$E6S7wV3yHlMgE6eDx|u3w6$B`dI(!vl0GcXdy9k<!JxW?s`>zu0`1@nU_XF(v+AnH'
    'En`LVtJyU?pHpUufpi+~Ss*hwDh`minGj?Erj;CCb1~hi7&>r72M??3BNXSD1RCn2aB(~z28%)F>ZUi>iED0QVzU{1gVofm=DH>=SDHqRI6<C}W_dWL$sdU6'
    '@N_b`<?3X_<XgLk_2D#*Q8k6mwsZd4E=ky7_kTeD(cJz=7k3bXS)O1RI&J}i``nJ{{K9(=FRUxVAi;!nRTeAyVJo5NQ%O7fzkfR<RI~0i?8mO82{Px}d2B}>'
    'C#*Y8B=Lhf+OB#W_k#%rt03=N>BP|wKSWzQ4(o#jf%bS~)|OG?-zs_wRAT>?bdYn_!0T^PtkO>w-kTAu19pX6Lo3GVyuv#BN+<64k=t_Ka_~o(%Pj~DLjGF`'
    'yGK}kWcRXpg<{b{PH4!ZrPRxIg&a>R!4yCRR@f+DhOJ<dp9)4DMHN<WR*Hb3)G)({ES3~wRUSHL6@<*81t^1^k+}<i?~rqy^o14~O16p|#k_ULxJDuZIZrR^'
    'u(T`sm{f`YXaXEqpnt994apI78Y&HQb3f-pTM5Lt<<D^0;pFqo-!MuvLIrRt!8_gHdCi15-Ko3uMk`?r&d-!;kNZQ%oHb{(0Vw_zc?G-vBA%c^k1LudNbm1|'
    'WY+oT^OLB#*=$8`F}K5u-n&SU{4jGHU2!$wqIb5tH}HPcL&wv5?gU5*Q2pB%-mQVqJ%qx~YPeha)3sUfXJk<n<R1MHRYztsS!EAj<E8b`dUixlYMuiNA;)NM'
    '7+Vy9uh4;kT|ZRL^+;PCcyHtChVmKZ6DEk9DW8!C?S9nYKORRvHXrKPV(mALxs0Fz%6PP(0An}Z5vzPS<x!#|aPobU%t`d0PJ7XDHg~%$8&dRrttb<cJx{V{'
    'LeL-u5!rjo;<#}T&dS^PJZdpizKEy}d`Y!OGCutJ^!c+3+l?{t7;i24DCln~-LbHsOc6r%Qr2iy$#=juFnP&WK)P+3BQYM<nZ3(;{d2q&_CVfyCnofMZ%oz~'
    'W?zZ<AneQD?AC;k2&drZuGurbwkSA-lQczEmZr!{)3nD?9_pr7aUR?-ZFLQIu`D(X8{(4ZzDxNz!(@uHtNMV5@p%s8+}m0zb`H<pc!Cfkg@+NB1$GO)nKF=P'
    'X<38=RKVqu9M9nbR5%Oifg)aDT)4S|_`3LL`5Kvh5OOslbXPdIsCA+4&?xmID@~)brRYZZz_5{V2o?|X7NlxOi;uW%d$WZX4MT-eM7*P>`DUYT;}>x3D3YAc'
    'o0$#dC-)+cR-<BvXmizPS;)bU0BEo^_)jz1h+H!4+unGc^qOI}Xqp%mM?d%Wj$4U8ApXGJgZNBsL-Gi~hMhXUXxs>xQ@CbUYzreglZV?4<=B!~meZ@@Xz&9G'
    'vk~8cQB4Ro0pKBVMsf3;w16OSK7Ia+<?a5#f|?zUYi5Hb-p)$Qw8CkM;}H0;J&q9A3hkAJS~aK!ratF9Zzl!i5A4~OD$Jh(;AUUXaj0z)Wl}@-py@p&tXTf>'
    'rQIo%P{h%fK$hNO=wq-8%C!?W97q=JDl7#~l(h@xnZKiKS0^*Y{K+Rdv@JTvaDV9&+2T#j^Avv$Y)jrS&aPB=klcO{_a&f(jhL{r(<lMk5jB?I%~mJACkEZe'
    '04e6v-LbZEgSQ!UQBK=zLVuL?X3ELTfPmNx<NBy33}=r>KI<azN7ppeYX^PGMd6PShClLf_#*`3k9;Klh@kkRVl4is1dQLB4WDbf10+grOD+XO35rH;HUI1X'
    'Vc)o}5|S(_@$1M$TPPD9XT8B~{e-~CPSA<#U~mnD167g#Z}jsF2m-3_@n@~u8(eed@+6|a&(!O$ATb?0%?r%*@Ws*5ukdJFe*S!X^fDp{9eMEP2!4W0q3Sq3'
    'dUN>XjV4O!BdS+r0KjKIalQ7Vliz-NbA0gRP50^HPj61#DmbSIfkZpGepHGd@>+{@LLi+2NIAVZNr13IS2V=w)p-Z-hf3H+Ka`A^M6?8|q!Hn0btswZf06X2'
    'R1T#AoMY=Jg`TqaTSKQ!dS4=0SQ6UWR?%{18}18Vx*y3-3|>WFH2=XG2iYmfE;6~6v{=PJ1$I7WyNvU4w*8<>-zuAp^3E5$NJ37^q3%u2&g@LkkvWwcE@t;a'
    '@#!1*jT^15c1|D*IoYjCcd&22)`@ixR&%=uG7kgMXh0etT#auMuzTC^lWx4TKK&t0GNSxn5_X<Obo3qIijn>=!$|)a7Mv$XSiGL{+H;^+qTvo0{l5_x0HhO|'
    '8?Li<qFktq0hg+$)7eDQv7|gtG<@laBC0qqdQKIRpLyy|BAtJ;mDE1Nwi!J3l6^YNZvraBVk(`}H>v5Dn~@re1<!`YXT58-F$|qlSs_5gbHGm>Op=@@P!vq;'
    'T8a-E!myc3zC0JWyAUuYn8Bh5sg?GtG{DXp1cyn#ot*?{c*&N|Z|7j*W6lwc>#-F7C;GljS0cM;ND?K?O&>RCF7>!cVy#!NuO>v|g+JS=(3I{e0C^NC`0>V`'
    'gncoUJe^Fq3nh8dJ`ES_s)BnvVUHEuvY(U4&72kmQl~|Yoam~mm*HcBfy`zkY!J|JK#hVyvU1<$QJmwb?ra0~+*Ptr75k`V$=82A#6ySH+gfc>9Mx5{PYub1'
    'N7#Dos28LM*od8k!uCnuh)jMpY^52@58@?P(e%fnK7laI1yUkf0~CLF8cGt7pyvzT3Fyh3aQRs68=C|R+BuYtW5lc7Na@F(G*RcDuDD+`|7LbH!YV$%6broQ'
    '`~&A{?CW-dsqi$IxwQm*BA}a|%OpMyo_~kF)3hKRmJ_6I7vjW~<DYHQj?{H$F)@7W?L`Bfmtx>2q%f0aG1~2_X0Z+CtN&VZ>EUY{Q?V{VT)LPpY^W>1<;Rt@'
    'R0<=$-Ze$MN+H0wq6;>wtC&+{Sc6N18O@QNP82;YIJaeYp}MDV#Ds<aB?Lg+53yegb9y)^thH8Ht(zqQaSc}OfwUeQP@m#aX&5FRJk_BdLBBiNkrnwWDzZW2'
    '*$`(n<CTa#kqbVEWNdF%OAI8djP+73SgU}_)3S6o+YX9%gwr)*{JNT__4R1ptf)+JcNL}o=c>RQ5xGGB<$X>Y+2~IE+8o+eQezN@x;Tp0?@Lb1P*Bro;OKH|'
    'aJGv|(bk~_DGCg3`9be(r|OQ*^RQe==-(x)C<*bP_0M}-jV^iAcJJcbx$GM{(YZ!k&7|pjPAi%F@@r}+A8c+Nw4ygELiWcxZu970*=$mO+k+*GUJNg<(0v!T'
    'V(m@$&EfG&4!3x5cyRm`w32TgY#rp)lJwNo-(gg5mola!X`x?2b_`Rnc(B#GD@?i7kv|cr{KqE4;7C6_NEvl|aLP{K^f|m{*~)EDp+Q;-DBaI<lB%$TbPnTP'
    '0tIc!&8=Ol2{jI+NOOT&zKwn+=$sKoVvp<phD|1Ljg!e>o=;PSAh5K;$O?#fr{xAhkPxG|y2&mHMn9Z}n(s4|QUa(!c4GmZ)3?zH0*asBN}{(xHt#E!<DB}('
    'u4@y8)7pyiXQ<tu(2lEkA4$tFU%<B%9Vu#y#d!vtd|(n?wznwF5;0Crx7)2|qf_AF$n^z87uH+gvcOt(;-c)E_EBzE&9P;&?Nkv+$JFP$#LD$x!#yr(hloXW'
    'MR!F5WBgU_kkv@jDmRHW&eg7xd%s9tKYxALd=NdmJ)I2)N3bsllmJf*fjUqpFca?}OPw-b;r76;bYC7lMYp}`VQ)6NeRA6$WmWa+_~0!unKtTZ&>GU{v|EoJ'
    ';2z`;pXht%30#5)KfO5AuN>DwZbe;GpA206bU4krM96`W#ko)$f;}}ORju()N((w>N>CS5Z!~J0a(q<19NDM_V+<d(ENN9?SX7lH<QH&O&Q@|#M_{@P0xNp~'
    '`H$m`cH5vpCn`;AQ@Lb$i7|D*?V!7STT-Xa+N!GE?IfkG>Dro3ZI-~9d#imv^0BH6B<FU72xDyF3rQbhjdBHY2w#H3!6+lw2$1-1dZQ0>ijIkDyU9+BQCS$J'
    '!Iqk+wuR4tIN`5N8{HtACJMb1dh=<k)vmrpOten2ZT{Rbf9}GcuU{OzGLzOx9^h-(&BxWw=Rn#(jMsuwO*4ZHcC_ms4KVLbRZvp;spjE`qkJfrF?rfYcuun3'
    '0HeytlSyU!gz2x}W{dhb%TO)mPJ`XMtw&aiThuq#GuJ*veqlWa_CjH-k6EWii+h?V_|t@x3m9!AodPB;!@wd1P@vT1xMO7nf`4$!@R!20<Bja}9iAK>$SeKF'
    ')8nJp8U!`8CH_5}N?NU*N6GHPSiPICxWtW>m$;E%;+JpvM!=BV47HKb){i^eN%Zt$2<*%-`ek(W@4@6c#!PLr(Fx)$!%QwcxaV%pvmRb2+Le;kfUs>S593&)'
    '&@RqrS!VAaTsNEmSq+RGBVPMabJHPle1xqlBk@R{j}Aw*Xe;gRHcqK;`w7oYeiA1aH@GkIi+WGnVfmJLxRX5EiWBHaF4fU$I|7v^xXM^Ax){zWNL0`EcY|v5'
    '9edQSG)2z#F_+LAicWdXt9x|zWO7q_6B#bmx(O5%QqyKI`;(iLEGf$_fJwWh$cYB)P6$HO(c1HzL9Il5w)WJYO&hHQGZV9Ix8Ix1h6sYP7=pAjxfyeC?djy|'
    '-8ogWN53cVFT`lRK@5B#&vs>}8O)i4D@qh0xql{v78RlEwO~B6@5m@STZsLopKXQ-z?QWrI~_H0G3v>v!(VPYUlx*I|FfNNg9I0wYcJ5nBKowwQmLI>DY+hH'
    '%lPGY{qoMWA>%@uE;0-~S6*%_B*vcJYQ%5ur_F}TGm?J^kvk>+li_7-c|(p79<eafX#me5VDCtb#TQ#lb9P0QP%w|CD9dEP20C$KSrSpZfkM1(C?hFztFw_R'
    'HQz|p%Q&6;%?2YO%!Ak!+C)Z7<7&>RqH)(ipo&@7x~8D8WY%FVDG!kelL9@ErF~7Ja{NRN=>Q?m2pT?qVi9&CyGk*N2?wT_-AnhKsuiUrOR1WdQ#?dPw>yl%'
    'C=SOaS_VIazwtj7`)*4|t}AWstymTi2#<U?CVUI0SYu)sgDwVvb_u_|k$WsW0YwRyrc4&rZO|3oO;;#P1H7RF*d;cES|SRo%9U0wMTuQh!Nzl|4(Vm+6)8si'
    '0?UVk09fNW>?S)f+Es2^JAYl}rfeSBTeQ%we>@fV2IOxeQx?T4n{Dr=v(Z?LUMZc~#?xaC7nvV(gw%X1uj=C?iHVE@DkEzHqRJ?@$EwP*Z>eOlZQJ`Fe=}jl'
    '&y@E+OMZpD+1**UJ9=;HK55V*JB<&DTihEFfb;Oub~kpHb|ZLH)|(eADnhXX1zkdxeD}u$cy$AS=ti88LN|>0Ye%mc&XU@#?Ih7oZ0Xr;_a{mW--*Rgtr+P7'
    'ZRq$5CqJK0wBXK<bRFX&#j3MTLCQtzl#lu56AjBz&R)9&Ep*;?mPhl`w@$PSJ;|LIVYzZe1Q`TF;;TXPbiwH{^qMB200v;q5Jk%SOhx;#af}OYsT}r#)-x}S'
    'xTIG2&D2V49m;)@!~0kGAm|D;s@W4MuO!bNdP6Z5J;?>UsqNwpP<`<}HmOo@U~Z}uD;}}<`a+;g`0yKjNL7Vypku4_0*s22@Z_SdI3o(4c5xx8RevTykpc-Q'
    'g!{?Six-Da-gJLHJbv^1#q)mwj}K3kK#oU~`2Hl~eQ__Hql7WML`$l(he5GoB8BW(tDnd5Sn0U9JWI7x0-&Lpcxx9uE``Ym_FZc^?$BGGky_f{!kP;BF0RlF'
    'u)JpHI5o;<ZJw<=O`)jO+*Pt}BwikdgdM4!`;8G1nI<SrN|+qX`%v_1MEei(5NNOFaxql-+~qyTT3d1>i^)-o<%NdA()(2RUc9b(xOLO-c!fAMXZQGgx3d8q'
    'S<FEI_&WB*m1Ndc?2FbAS9MkSDptmq&ySCfj_WU;|9Tibc>xFD`OnV}kE7aYcHX-l;+7hZZubxaYnJs<%15uHS=PIle+4_^OWzx%KSC?r*^nWrE{3=Px})KT'
    'jDFJI?hb&x@$pBXB4s~R(4&(XEvQ=y1<lC^&tJWQffvsH7j2()Tvsf~!6x*2OiGAfHYWQ+SNy-@ta_cZ1q4@?b-GL9<z%LX8AtLo(F%&gzr`P7II}@li>ZY>'
    '#$ZsZ)$6U&UQ<``c;<Sa2Og)Qw)QRH2+|`j8!lS^g5d{d)mk>1TWSmCw%zb&8VOV{ei6%Vm-buXoYJbLc*)0RE9oxY*ODrNtPbvSjHlrRnacW@m88$IL2n*)'
    'FM3_;(NenY7T<hw-W!fz_NFz{-Nbatd>XGp<ncR&uleWrn9xo`u=e`T&yP>uM74K79|my?!@SOh3xYYF_J*@LIeX(O)Nw0BDu>7YUjc7_+V<{%Sw_lbBv!E$'
    'C?VDK{`CQj2DPWP%1_6?y?XMjd-D3|O(lt(pXiZX`RU--!{gtBuU<d@*T3MnJv(}huTNec9ld$>{E#2SpYP#TFzl2b)Y?9glwCI!wM_1EsbEIw3ONnhS*0s('
    'R%yl;L{88;(7fDA#x=JOeQ%M4ip`}mU?E1A%jYU{4GFDgZ8(fUzqtE4eRlmlxqXk4tQewF;c^u(P%oIRgu+My1YcrM){7gdSRO7FCw{C#=d%*l|4>_2Mv{gT'
    'aZ(`rtQG=dg{<W0yE&kUr6@<UQYI9JMJF*F(I_~EB>ocb!9x0ebGl6wdnsjC1udFx#+q1XbX}^BAC{8!uf*E_{Nm{C>wh9J&2<)`q&ccn2C7lk8`Q~mSc4v9'
    'v);(%?{$JEU>1AG<zr>X_`Q`lVa5=I3NDRSgWRj8SEr+4U+*f#*Pzj7(VHg<xfcmjG??{nc*9@KDCOY%>Qo?m$*UAd1marvX2ZofOgL1F5g3@riEx15qKk^u'
    'N8=+9rqe7ND;zMChQ|`{h;Awx#QQ9}p+55o!pB&sI*%@|CJU-?jyg;9j+se<Df|th?vR{=dr%v!U!oHANq-5i8$O~IX*v`XFpZfTL~o|65sL7V9EGu>7Ux4o'
    'kOI2jQ~6oQk(*^`)lq2?E0pvyw}?018zMS5P9#WYqv5~dyIGG@c4p(jJDf+#bv5gu&$-HV)f*E4vRd-`e46z!OB${H=KWvqKmXGJkW?5_1Zlb;&EhqyK}qlz'
    'p^xAnhrj$nzn{PO75|H1C5XF;_2D+}zJ2}*p(Bms2F-O#wgtk@4vA3djd6x_SbzQ!K9?Mv&a*Un^yrbPloi?Y$w=qU;ray${$@BH!1=<poDJW-L$@e8Y+UJ!'
    '!-J>YXUKAIMP5H~-?$se-5^}S|Niah&7q7`)nQdYJ2!$&M8}N+Rte2}MBo~Al-kGd7I0K4Tn{UR5fa=R4)cNT5n^~py&C}&r%LAi*>Fn8;cPGF&m9k4`0cW7'
    'XCJ#~2vtrIY9CGP8vIR@rmey7z!EaGcL09F;;O?E8E8PoMO7*l!9$hRU?Qa^0K=e$lPf-2e9|yF3MpZ=vk4!oD0+gplZdMd{;b4h!n;PVb>SSa8cK4SU8@qP'
    'c2`J-EkA9cd_DGpOxlVY>9i}FhAKvY$R^@%Kk6bG?c(p6v`GA1CviFu=fnH;L39Hb`74g1sC3+T<bB{<{EVzQojaWkoU3aIYpzS3)*$4~293jQLzPCZwNo6x'
    'Pp#zj;IOV0TvuqKW{;oawqw!{!k3<$sdp}XZ12sAr$IpW&9s0V;BIp(goY;2307HPt#==E3VZ9p5ZXteFxt^R0V{1#B`GiuY!@RL0rr_E6m;S|zC>tys@<aT'
    'SSv({5Q>~U5RpO*Te;97jvS&r>1@c)xd~U*;gmmmuw=${;dX21VQ9)#fdKZSMxKov>Zn|QFpjLzXcZ<NRggC&qEh+CUnZ#d0!kXaJosn#==ka3@kx2Rz0nN8'
    ')Yc82$8J^7YCuw%CBwv@*T#%d8%qh3D_~9Kw!6mTFT($_FuW?{t_f495+ntJLdqwNJaP+Ao4KL3G@{JNcs0`%V>Y1@X8M_m;3j)DUtZWR`bO=`dgQVJK#>vB'
    'j82)Xq#(Um__!-jef3)H12@T7;Z6$Q03>3tZR(O5CxDPx#TOc)CxH+_nGrjs08}IrT904zd)DyX>w&tk?{IfZyM1X)aycj(r}E3yE<(6PXf1I875baL=JfJ9'
    'D^JKLfzoi%xvpSTH_pl>4j(2OAH>lQv}*MC((Wm4GY=wTobLq!t(im$trquuoG5HGi>XBbHNR0qyT}iB(Q!0TE)6ToFCI{s5YfpY?G&gy)KE7{!Obogw}Nz2'
    '04$_MJ#Ra}cl&vNnf#1Pgy(RK{>#{lwxXQ^8n(E#)o&hKLacO7%i<Lx9-9k6Z9dwK?XTeA-IS6!&Y12hZ({qEVFh&9XuD<TMW-PDI)eQFqx<aWw_{FJvztWC'
    '2k_62@Xy19au;oJDuI8H(Dac1v}F#1XMepKp9IYQ;WY^`brIG2=T~Dy@X;!f7N;-0nxYhU-W#2%6kL?fhdaYyBnAx55&wbjyck|xaOAHN?6atUHJhPIg=T?s'
    '>)~UT*@mKM5E@>nZ7|Zxsv^lfuroD{9%(L1wQ~P=u`}y3!hbVAdFDs!4VH|;ARj1R$wEHhTl2r3Q~FP`9RGdH29e(Xem-MpG<_?v4J+^^*c!}RZ9DqjbRycO'
    'q-i_xpU<wqb*$Kx)Ox||p<lXSUV%CkHxsObUrHVS4a^P<p*$q&3vJ0h4zz0q7P@MYmJ*L7<|3T3Im+z=JsWglH&RNmBrP9GOVy^5<lt@1WjWS~r9{jN1b@pF'
    'AiqdA+oHxk=h1#b*lK3~h)Vg6%4wxT61}eNZs?ljSI}NB_kwhp`#@qh<3FHx*Sh`#Xah=D&@|pdZ%uO!ClTsSn4yQ4_th64SnAHK8g=?+Y+)R`R}%C&$mHg+'
    'StmtTk99i*ZXRe{;~&G{YhWMaMy8|WoITEKVyWv}ObnOXCgQ^IImH>5SEblzxY0=e-@@?}*U3ui);jv^&-b*8otZPh;6nCc$x9s)px%}I5u}{uj-Wf2SSNm6'
    'Zv^;oi8I2zJ0d(ic>4++5eB`RaiQcL)et#vEBf}~UL<Y_lzKPkjd0Hv>8G!a76MKRCd-ZGv8Wy3PuH|Ln3~%I{?@k#{2j7n!sBAl%GR9(`bQ7$LyT8L|67dz'
    'Ta5o(jQ?AV|1-pRqN{(4@qbk@Uf*@?in`_URtLAx*ReVjVtWUqZk4PW`t?<1>~&=3q9`6ccS;mpjhS%8Jw4EM#XS`@QOc4m=aStGP{1Xx?xG8Iti%yZIg2CK'
    '9Z9T7S(hV*50`Mn-Io@V*hDT74r+4?{@IS@t?-I3eO~dxTHXt5c`w4e;>BN;SA6+5ulP5w_&2ZkH?R07@`^A2<`w_Syy8p41zZ&Jif*C54zKv~zkpYK>GO)K'
    'F%vGY`0`76#fvZF72OT+#k}IhioD`Qj#qqX@rp0+$}7Hn{ikbBfiHRb{B;Y1^6HE8tUee{i2#l;)=?mQDT=Q4XR1wqdP<jNq=OXs83)Zg<R2<jg?~LgJb3!z'
    '`789^dcaSf9AN0lgB||mgp<H;mybRLW@<Vb5=<ccJ>^6Z<_N&E87yUQ&Y%YHGsIrQ<NIc>w{~py`oW`yO0T;@f{_3<E3)HSjFN4XRr6+NmQzN?PZhlGD=oML'
    '(Q3*w20vkXD$uunri`ezqrbGg%t&KjxN0xB6pd?hgEY`^LVeO0!Zo%xQDN`iQtto!0kSDO54}5Vkd3T5+pR4Hm3DVI#9H3Ap0kcO4#jryL9EST0I~9J=Dyf$'
    'shk9~hr0|Zr?bQaskI=N6>DaUk_yr!Sy=_IGVvzo#q0#qM^OjtB9D2`sI%w=|Hz8b$IPQ*ud$0TOlZ&N!!X=3brQ|49^0%bh@XD8H0*jmYI65*pwN7PF*EFw'
    'vxG_XFfPjDqS0`j?k17h*&grXSOWDXse4?Fz5_KiYga5f72tz{dv8As$7e6AGD8;Z-u+0(?O$yV7bgT>#-}geS1Ml-qhra&&xZooVi^?;$_wt<P`_Z{1(Lxz'
    '$H7tNRE+ye)C$OXw6^6XGVNOh$bTrag@fH3CjicliY=Yz0^ExCE9}1V;<Aw}`ceRNQ@k&YhfEMnz&#ms!&jC8%y}O<tbjkNrNV)d2Y!0`b>)GAtdN#0kYoS#'
    'Fctg%MLdvQEwc;`RJ0Ko^i14UU?^p>mJ1B->VC1n0ClV+Fi1H|V9*^&tVvl{V1N(*Y=Hrx$6uho1tQRn>ZiCL$j^eJ6o9!zs*92IKbT;9Ej)Y;RJYf5(7y`d'
    'cLV)(KtC2%s&)poVPz3&+qbr3Rm4}af3yYTkG5p&IPh`x&rja?AtYE1!;$$*QMFKHSxe<cF^CoY-XH_|){>ao>^g%jv_r+=8bw_jOfo;++Hpd*8?N;59em}T'
    'dMcPlE<<JflA?;#!BcNw_bu`?cRZQr0mJ!(tOoyF#cZ&$(4+bKpm?HV>AQ@(Cd?htS>vcCNJyT7-!3acj#E%6v(*L)3S3H(`c}YH6#NA57Y8532S#yF2(Ym{'
    '4gn5qOu>~Zo?3<)4ye}0?z1J6LG{eQSnvdC5S}1VkuQC5pg;DhJ#-@dF~%PQ{By@D(JcjI{oO!+HSP9P4+*MD@#~^=9mHXwfwbL25*?jLeOr8#GVRs_%W6^X'
    '7+GnlVQWvtPoF<KRubbBC>VH>=HrfrF^^4_+FChrc@>Rz*^1g@mxa;JrGa<8v#G~IFEPq>{nRJ9)a=~#&nsKVe5drklr`)NjDyPzSE1!xX1S8tXQ=<>wt?Pt'
    'Z#WVH9k56^?Q+?bOb$~aXe-&oxbS{HH9@{!rn?p)B>)gUR9>mBCB4#vc73PSQ8KLcgd|z6m_*seW+P<pdQgTh$~Z4M(w!eJPfq^|FU7Obq_?PbXWKt^W$kFH'
    '<TI!!NB)pHVZ18QXGB-i1KrR)t(P%9en+IX@}5{GFx7+DNx-`V@iV`Syy)2WzRX4)rhPY;5AH)IvNml!Z5~rYCHXpkMbLKz%9SvhymNGl4P{uduSc-BRy2eZ'
    'MRW&?T9PeRy_{w<z)msE)~4T$K!sn`7AJE@sgR8+?w@}-+1o6EvAwM*V>opXt5_gtn{nUWH23ifZFBBMy9evs$5qX9AM^IPf7%ARf8N<b_vZ&VoIHDe_~L0D'
    'McY<%b_FcVnTp&W4=;M7A4bU5kdY4I)QJZgjy}{;e#HENBTO-V-(vU4OUa~2T<nvhx4@_FG|>2S^6c>NHT>G8U%wn3ogBii?MCA>fA-?w)l>F#!vb6MZ}^e~'
    'Xn2joBothd=UtTC=T8p1PmT`{UKZizauuSv6^(!b`SY;<Y^*;60cfBC4SXP5AmI;_OGLHgDhlQoz;$5;2|Bp*3v-C!?~uU|9xs)ig*@KP-siw_72x-lV)rUh'
    '!6nt>+ZsdeI_pKrN=eC&pMGsLD(py3uOFHMv|uln{R8>UDwN->BKghKgwpLr%N+=W<%}ENl;St~(JG#Q#d?CvtKNXtQ<7?VYlg39z45|dw|;Mat{E)z-38oY'
    'w;bjSrF94@8y8fQ#YPlagvlz5)>@H=BwC~-P!{rHIgcp*8|T{PdeI~TBPwHs6}J{PgV5v&a}<3qlUOcJ*m#ASUCQ+$#~)EH9>)g7BzD<+Q4i~BWQejQI|FHr'
    'q1z=MWcg+>>+Y(JeiHiFiqLggk<Atmc0*3_GH@v{mTqVW)>ibe@!9Hg^A3G>%yrAVom)nwX;`~qyw56LE1c;%mGfHnd2oBd@bfm6CzEIcWd{CyKiXzl5N}6O'
    'Q)EPb>R5rHgxUXT?plA_Hj?<iLgYS>tSO(QI&LDL3fv{GBH)tr>=p<h2(&EIGGW<NMagzz<bS`N$3D4~C_6sfhc@PF-;bH!?99$oZT~!ka4IGy2e643MPrYo'
    'Z?I0&EjAl&G}-u;Am8XHdTj*gqJ}D~9!fnBW#@qfrGSLx;@BPaKKOBrmT+@kW_^%9oC^?hPO25c4C%@oGALKTwcp*tFKobn7jnMLCfBwFuOVr|G-BO<XB!r@'
    'SFM`zHn?GdE@(pp+w#(sCb2m%H2~XBTb-@}&*+r|H*96Ft0d=C#i+^liF)w>fe$gFaZdX*Ax5O5)5&R858TVuGJ?Yy?+dK7T$SL6I)YRB3K)d3GVYDPwB;17'
    '!qqZui9MMtQhVdZ_MnFF2`B3RO!ibWufp{<M6I@XsYdox>2f3X-7Z|(8|c}hrKqEkWXbsq!BTZ3F(zeKu~HOlBvl5#9rS{KqdM!opr+Y_7+P?im8;e=D;Hug'
    '8HM}?;V??yeR)q>p=@5H-NVjn`muFh6xVS;f*j9>pajcRQOs#JrVkfs4*e1}q#r(?)@)z=`M2ShW0dE@4?_yQC=rDGn;?n&0)7XvW3lkR{(L_;hT7i%hokyV'
    'K7S-#CVnaj>oJ60k#{__GQ{thSO)mqmkAkI0~s04*B9bMq*o9FQ>SvsACd5#+d;MVDRTi#p_OFIZvH_@ZcvHl1{?uhoS1pBf`7nYUlLsA4-oD~xd;5rOM|Zb'
    '&M?y%MGiQ_f@fT$MSPGo7?=4Rg?;k3Uar_5d`>Y9Fq3xOhrCNgCk3WXYq`J3mN)Aap0YCHZlVn&^ul@qL0(cwDwA>7-2flCR^VY><WiOO9jg7Yqwh<ow~*&s'
    'zR<BndBR-#KhY6T^!2IK=DMI`&V+BP24g*He;R68IqV3~C07<#?7|ZS(YpVy*cEm+^TVnF&kn&`BtZnfBxJQ9$T|YUN}LsL{=8Vvu2xmmnAV9E7EE?DW1)ek'
    'L+Nd~y0h_2B>bNNCo624x6yM%N7%`V+PHqVp=%P`<na;pP9_v};GIHJ`sbmequt<CZfg;z#ch!X$<8|o7-Go=8)7k8PHswc!+&t_HKkA3lCiDtd%W(M(#jp{'
    '=&zID4v*q?bzmGzU&-H<AwZjJrYfx(MTwfoa!xf>8anEYz4txFu9ODWU|NL7;RdtasP$(u4FRyxN_<3xwPE%wCok7DZ<iQ<HKp{3^jR`&Xu^{m>n5mOWv2}!'
    'fr|pI_uOa!R==blv6f3diqH#QDKL<NI9EhDxjKum!cSU-ua)~58_~A)*_x8s=~MU*??|kn&&06Ydj6;nHmVY}Q1Y*V!Ngs!XqtJCDva2tmvST_(EwVYoAd8J'
    'BV2>5h!eZ#QQVy)ORy&w3ne%S#x6CxN%#Rfh<~c1Y*th?RrSd@Zq<Zc%&}LpAe_M*III@#o~?q1(KX|C8R~mtz&Hu}cE$EJ;)oH1)ayV`&w`2}DyIv?5IHe@'
    'M0skF<WI)Nl1UzYS%a?q$|DB^>U2>GEe<|-g4|NsZ?(ZE8%Qlk1xRd>i*1W5GJ_$n=nf=$p)Gl(g7g9X%ley!6PEJI>t1mD<@bY5JGc}QMh>B)mceWdaj7B*'
    'ciedsoMqx?DtjiylJpqT9QDd|zMv(h*kJf4#<Fq)^kU&Ag12sY_d{YdvU6NTzeOYmnnpa~Ra%6kw7@JEldo(5j}{0AjeJ$Am?q}@_N=eb_1Jz_O<}17OEp0+'
    'g(hdv%c0HT;slwynGr*lhqgMxQ6)_&Lb%edg@jnaijf+Rdp`OqwKn*^3)C(c_*#gUpN>z`Pp6|WozBI=r5MCJ9NQC#s-2KkJ4s+qGF4}V$kj5H=qeN*$tlpo'
    'reqp0tdQ7uw=>tYYP+$Sscs@_vOowI&@*tnP&DTjZ59cBOmJ!Mx}CQvwULTl649Rt?3mb+<v3cI*hTQp?&NhR9e(=#&p*h3{}kJRzG&A8;e8<(&Jx-bNpVFa'
    'o8Da5$e%*h_n^;e2IGo<O7WAj$5z?EwDKrefiL@hKvN4JuxKI=m<{5;?Qu1dCUm2+r4Tu3i3;js6)MHP6W=t(DFhV8$4U{$N=|~1)EZ$dAL!g+V0ejsbL>`5'
    'iaXuvNhm!ac+^U30kz~+xo%t$$%_;-zygX|TAdg+6vssDb78@-fC}sdT|qGfaRgdNS-h`|P#A%1I2EL4;H^a|Eb_>WQS%b#E-#572mqSWhu^WQSRQh|@C(FT'
    'h~z+#irs=t0%IG)o%SIpUAhP8oMEzD^`-BInrBPb_mU-iZTEGxDA3dGWe5&G?!_7{shK{^6R7#rM9Uvn1@waDX>bjETimD6e&1uNrmhrFLki=kHW!oC6?X!6'
    '&o~L{Mw{^bCCCqHk^A`nB>3s4>-%`ru8EC$o8AA=MuC`c!@P^)ZC&6^#!tpbR-WTo6P@$!IVe%HkBBzl%?ut`#Yarasm;VH@3c&w6(TlZ6m{hM#%Cf#(jdc%'
    '!g7a%9=zg+%}Ma48n;$TyIb%Ri}xf<{t~5{SL7<j`Ax+BCdH;Lj?qYaUU*L&rcV>q7VC=ypT9f3aRaz%O~kXXCPF0wn;JFQXj5e|;HJ@m#KKHlA*XI-SIl`x'
    'n6upt<^T&yP-%&!HUVe5TLqjVZ4+js9Pj@5?t}6pfGIXeovv4g0%dZS0RS)YQ5~<f7HoVbLD;orb|dC5znv-GZ9W!4%Wu$)ktKMD-*9ZMGgyWQzb#W+vC-f+'
    '!hLcOYR?&IBav-vshW+;2d{ITUpjA1cD~7Sy^9nW-}D^3p%aL|m~VZju)OSc$5Be|QP{7J28V!1o59h|Sk&{lW2$chr}DlKD8e5hr_oyn4?^I2-AP4VW@f(|'
    'r35XD$W8eaSwwB#|Gg~I%uBwW58GnZCz_~J)w8}TqKSSqcGx|r6%sbx+9$PAN!^PVt=_U;z4)-A>wBQKhr0;`iaHR@t)~~d$lrqhtg|%)Z59MqpjEg51Jwrx'
    '?`CDvGN0wQ5a4!tm0hgo*%4@a#Bygc*zHZQDvEtyKdhtq7qkSUmh_2V5{Kh`ynZXASgNTKI>%UI!?W)nbtYd<nnin!$vMg@j|=Nc-Y;5;^Cb?y;KlT`NSVio'
    'S)7h~-7(28G&%t?DiSeIVa<5IyV|_bc!N0lWH$*lM?p=72ly@6uJ1@X(r_)UjwnJjJ2zN;RS!S(ZfoflMhh%re#2&jD!gzM>;4C{T?0y|I9<@U7G`dYMKzHM'
    '6$BupB|eXw92ys>EJ6T^I&Cz9!l|V-B`(=**E1{1%?sb#<eLF6cFo|iKvv={?ioz4FFg!xT`nfeOh_RDyFl;N67o|h`*#kzEXG$SNx|kU5ZsDG05d*T>x5$;'
    'jVsz*pJva1(muYUmd1o&Ufi#Es_&w`Sg#skZllF#Vs25B#M}}cxR{%>SeRRNAhEDP1I#U3*%5PpJU$r+L|IO5vKHDCf^t=i=VrkZ8sPwo%b<Js_H|eW$3Opk'
    'ps@GHf&1isrctu^TM*|N-SUbL>%sk?(KT->ioL9%{SS3byHz_3@q-K#ZAs(V;?YOvH(GHQuFY%%AGV2MDO`y+1Ko+}R0FZEnp@{6OTaLEL1)&h5&SgDSK~4H'
    'o<aWLBzxWjTa<hY-S)r1lMS$qePIzU5AESiQ>8sVg`nEzqgQf+TPABx2HN$M!`vP%r)wKDgOo`g12_dQ{jzP~K5T1tlAX6}gXcb7n?3L4nzatkf44ScA}$xe'
    'd9609JXRYRZ`B4(iMOnMN76kU1kw5W_F@jU0*v0Tih0(W&Wm!r%p{Q>4g`ES1y|&k%i>#h3rd5?cqXNvPB|~F<O3{zVr9L&LYFH;gZw|f!XBg+r)IZ;-?C*P'
    'l1S6dX%JAiCJl`tIEmMg4gQ7=*+xDC9a5R4*r%6g9`&5!X?#MN|46>NlY0O~UbMLRi0+C_)UIl@P5op0WdZM<@3O|bytGX2X=Ux}Ch$MwV_0PO#}<krlWQv{'
    'lKj?k=(@&WLXl};2bCsRXRNs)B$^x%zCDgFFqxfS@JQo|0fE>;rPks}nFov7FHDFyWdbv2(#e}DZHPf5*{sX_JUPIiUshS+#j35E$LhRV>hXY&+4A~T;WSMA'
    '_Bv^zO*_3xsSPE7Seb8H==kf+bdl2{+uJL@y~rL6D^jhr<feS~ijdj$Y67h*TR^BZ-s%dwxZ}Hmm)wHdMWNheptPx8cFEqbV_6)}R=cnjxCaK3MZ;edi>Phs'
    'mT?M4l+9y&D>LAPjg7_II;Fh2_Eu9%yw|6N6(EV)R)kX#oqnTdqnas=yd25GZAM<3M`12Xs%EuW7iOiT+N{LUFsB^xRtP9}vu11gi^D*?%VmXw8igyE>*4YJ'
    'c-w`6!{@@l2K;+F7&MmQ*+?*#NHF&z!MuV5hXxWHHb#Q^4oL97(=-04'
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

_FD_CAP_MIN_N = 40   # v12_14: the base's wheat sales are capped only against rivals churning this much a cycle
_FD_HIDDEN = {}   # v12_13: seat -> wheat units of the fade lots (restocks add, fade sells subtract, clamped to the shed)


def _fd_hidden_clamp(seat, obs):
    try:
        w = int((obs["private"].get("shed") or {}).get("WHEAT", 0))
    except Exception:
        return
    _FD_HIDDEN[seat] = max(0, min(int(_FD_HIDDEN.get(seat, 0)), w))


def _fd_cap_sells(market, obs, lot):
    """Cap the inner layers' SELL WHEAT orders at the wheat that is not the fade lot. Returns True when changed."""
    try:
        own = max(0, int((obs["private"].get("shed") or {}).get("WHEAT", 0)) - int(lot))
    except Exception:
        return False
    changed = False
    for o in market:
        if o and o[0] == "SELL" and len(o) >= 3 and o[1] == "WHEAT":
            try:
                q = int(o[2])
            except Exception:
                continue
            keep = max(0, min(q, own))
            own -= keep
            if keep != q:
                o[2] = keep   # a zero-quantity order keeps the later slots in place
                changed = True
    return changed


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


def _fd_drop_reserve(seat, step, pinvs, horizon=3, per_harvest=2):
    """v12_12: shed room to keep for the goods the route's units will DROP within `horizon` steps (the fade lot is sold
    again at the next phase-0 step). Falls back to everything carried without a tape route or across a day end."""
    carried_all = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)
    try:
        ns = globals().get("_BASE_NS") or globals()
        chassis = ns["_IMPL"].chassis
        native = chassis.players.get(seat)
        if not native or native.get("route") is None:
            return carried_all
        reserve = 0
        pending = {}
        for t in range(step + 1, min(719, step + 1 + horizon)):
            if t % 24 == 23:
                return carried_all
            tape = chassis.routes.get(2 if t >= 648 else native["route"]) or []
            a = tape[t] if t < len(tape) and isinstance(tape[t], dict) else {}
            units = [a.get("farmer") or ["PASS"]] + list(a.get("hands") or [])
            for k, c in enumerate(units):
                if not (isinstance(c, list) and c):
                    continue
                if c[0] in ("HARVEST", "COLLECT_FERTILIZER"):
                    pending[k] = pending.get(k, 0) + per_harvest
                elif c[0] == "DROP":
                    inv = pinvs[k] if k < len(pinvs) else {}
                    reserve += sum(int(v) for v in inv.values() if int(v) > 0) + pending.pop(k, 0)
        return int(min(carried_all, reserve))
    except Exception:
        return carried_all


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
        _FD_HIDDEN[seat] = 0
    st["step"] = step
    _fd_hidden_clamp(seat, obs)
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
                    _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - y)
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
    lot = int(_FD_HIDDEN.get(seat, 0))
    if lot > 0 and step % 24 != 23 and _fd_rival_n(mem, step - step % 4) >= _FD_CAP_MIN_N and _fd_cap_sells(market, obs, lot):   # v12_13: the base must not dump the lot (except at its hour-23 warehouse close)
        changed = True
    try:
        shed_w = int(_project(obs, dict(action, market=[o for o in market if o]))[0].get("WHEAT", 0))
    except Exception:
        return action
    if step % 4 == 0 and step <= 716:
        n = _fd_rival_n(mem, step)
        if n > 0:
            _FD_REPORT["active_steps"] += 1
            reserve = _fd_pickups(seat, step, 3)
            x = int(min(_FD_XMAX, 2 * n, shed_w - reserve))   # v12_9: the rival unwinds into our refill, so 2N pays
            if step + 4 > 716:   # v12_11: last fade step of the game, wind the lot down into the lift
                x = int(min(_FD_XMAX, shed_w - reserve))
            if x > 0:
                x = x if _fd_place(market, ["SELL", "WHEAT", x]) else 0
                if x > 0:
                    st["sold"][step] = (x, shed_w)
                    _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - x)
                    _FD_REPORT["sells"] += 1
                    _FD_REPORT["sold"] += x
                    changed = True
    elif step % 4 == 1 and step <= 713 and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"]):   # v12_11: no restock without a later fade step
        st["sold"].pop(step - 1, None)
        # after the rival's unwind the book is at its low: restock the fading lot (XMAX above the route's
        # pickups of the next steps), within shed room and cash
        want = max(0, _FD_XMAX + _fd_pickups(seat, step, 4) - shed_w)
        # the lot stays in the shed for several steps: keep room for everything the units carry (a DROP into a
        # full shed deletes goods)
        pshed, pinvs = _project(obs, dict(action, market=[o for o in market if o]))[:2]
        carried = _fd_drop_reserve(seat, step, pinvs)   # v12_12: only what the tape drops before the next sell
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        cash = money - _FD_RESERVE
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want > 0:
            want = want if _fd_place(market, ["BUY_PRODUCT", "WHEAT", want]) else 0
            if want > 0:
                _FD_REPORT["buys"] += 1
                _FD_REPORT["bought"] += want
                _FD_HIDDEN[seat] = _FD_HIDDEN.get(seat, 0) + want
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
                    _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - y)
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
    lot = int(_FD_HIDDEN.get(seat, 0))
    if lot > 0 and step % 24 != 23 and p is not None and n >= _FD_CAP_MIN_N and _fd_cap_sells(live, obs, lot):   # v12_13: the base must not dump the lot (except at its hour-23 warehouse close)
        changed = True
    try:
        shed_w = int(_project(obs, dict(action, market=live))[0].get("WHEAT", 0))
    except Exception:
        return action
    if p is not None and phase == p and n > 0 and step <= 716:
        reserve = _fd_pickups(seat, step, 3)
        x = int(min(_GF_CFG["XMAX"], 2 * n, shed_w - reserve))   # v12_9: same 2N cap as FADE
        if step + 4 > 716:   # v12_11: last fade step of the game for this phase, wind the lot down
            x = int(min(_GF_CFG["XMAX"], shed_w - reserve))
        if x >= 5 and _fd_place(market, ["SELL", "WHEAT", x]):
            st["sold"][step] = x
            _FD_HIDDEN[seat] = max(0, _FD_HIDDEN.get(seat, 0) - x)
            st.setdefault("legs", []).append({"kind": "sell", "step": step, "x": x, "shops": shops})
            _GF_REPORT["sells"] += 1
            _GF_REPORT["sold"] += x
            changed = True
    elif step <= 713 and ((step - 1) in st["sold"] or (p is not None and phase == (p + 1) % 4 and n > 0)):   # v12_11: no restock without a later fade step
        st["sold"].pop(step - 1, None)
        want = max(0, _GF_CFG["XMAX"] + _fd_pickups(seat, step, 4) - shed_w)
        pshed, pinvs = _project(obs, dict(action, market=live))[:2]
        carried = sum(int(v) for inv in pinvs for v in inv.values() if int(v) > 0)   # v12_13: GFADE keeps the full reserve (irregular rivals)
        room = 100 - sum(int(v) for v in pshed.values()) - carried - 3
        cash = money - _GF_CFG["RESERVE"]
        want = int(max(0, min(want, room, cash // max(1, quote + 6))))
        if want >= 5 and _fd_place(market, ["BUY_PRODUCT", "WHEAT", want]):
            st.setdefault("legs", []).append({"kind": "buy", "step": step, "x": want, "shops": shops})
            _GF_REPORT["buys"] += 1
            _GF_REPORT["bought"] += want
            _FD_HIDDEN[seat] = _FD_HIDDEN.get(seat, 0) + want
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
            _FD_HIDDEN[seat] = 0
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
