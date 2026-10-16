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
_BASE_SHA256 = "8dc900723f900b1e37781794fc3d94cb595988c2ab390c94211d80578af02e33"   # upstream cha22 127ed3e6, patched: see header
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
    'TgN9n!J#H!LhzvKNzj>q8@(Zz=A4bpTgR9li|npv<whI%e1%5#wUf;tSg5RU`XA=ry{m0qX&nClthK*`OD~Bbp-H$0OiLl9v_L4Nx1FY`lQ`fK;xtZxK<Q`y'
    '%|(*sTcCTN^Stj~=M=}5Mx)VaG&35F7B;d!%x^c}x*tD(dA+{3xY9Z|k8Z9vcHeyN?R3^x7M7olkC*+W+4Gk_?W4_?#ontoqs7Oi_U`Rc@7M0L!;{TYsr~fl'
    'r^>IT*_YSnovSZTv&A<{TUV!RrOTzt;n8SuwP4M@_%T=M{4RX>QJFjRAAdP+RrV);e|xlcU3<3vZ0X0w?a}9()&BeD-qMeL*Z#fqwB2f6on1WHd$sgsVy}6X'
    'Sy=kI?flZ(?4-8$`>yo<V5Rxy>8JD4-stvA@#K2p=2!pQa`iZ0d@(uvbz?rBRQKNQ-!2u8KY#eP_tQSepKg?vZx0S$ynb}~{mtq1?XS1Tn;&1Uy|!MR>_2_G'
    '(DqIipS~D>c;%lx@e3O_rOLwDt7nTh?(6GM-`kVj+oz{<v(>jNyUm}k*Eg@PULS*Qd~CmY{ByKcxgM|mm}EcxoNR(PdNDreS~r)?{O-;8(bfCe?H@P2OMm#G'
    'w0?B@es;BRd)PWU*xQ}keEe=Lzxnpb?DgaJ_iCrTVK*Ny-gpOFAJ_a5Xar|B?+O>kXV<IWceB6Ui`wKx?PIrhSzDd#{QU{c(CXgn)%D?V{@KRS!R_zP#ozhe'
    'x77~|{k_TR+WWcpzd)?K=&dfT6kpvIz8`pxMxS3VtZ%=q+%2E{>U(GH*Bklm{^|bko9%n8$A#nD@2^j1^M_|Y+ST7bZ(dnz?)#2y?w`MX11r<h;>FdeJvTcx'
    'kKSyZEmUuwzW!KStL?p;eYSGjy87uXSg)O(55KOL&Ce}w>0;^SY~kC&w>RIsv%&UhZD7u=ynWLCx$^AYucyDCp4wkN%oPq+9)GHAZ!NV-cJ0Zx(@!54j@tW`'
    'pYI9>U%vgSbXxlhdyC`ktHPs`7hlYqldD7P_m}F<YwP>^PP^JaoNOJh<lWNb=kE8y$<l|5!=oR!g@v0fYy3T5INpC{j%$yLqu*QY_Ncn+y?n9r@l$u>rd7Q@'
    '?LK>1`o8i0{r-a4&Q`bm>gd_uPlt!E4i}D#=bu&<_qJ{y?Y+O)T+83Sc0N2?9%Rqf^7|{MTiSp7q<X&c=<knbTfK$x=e6!esk6V~yq+w5di;HRad&XDV*Y(n'
    'I^CZe*EZgK-@m^8{<6F9x%R&G`0?CoE8FtlK0f?VwfD|Xiq<AZoa}q!;o|J~M}L1_|M_~qvbgi{U{D>Jdxz%JH#c_iduQ+6<8|-Hlg+<><h$8Ne*Wt0`=;}1'
    '>B@h!x#8Zt`CQ%p_Mx3$xVzdceVDB8UGM)`^-J$oN-GC<vmf@H_T1v*ANJ=*R`!{<TRXk`&~oSYe>^EIfdJmwvx^J2hojR+zsy$`oyptR7f(jjr@i-&-d;c6'
    'Y`r&MeW*Um{>To#eVVJ(x;NSO+4(sC^k`{kE?@cfv$lKu!#P;FoOS!VtJ&Y)`<?X{3)Rb)i>6uXcP3B!t>M;Eb!B;O^)g@F035!o&t9C^Px3#S-sGA6t$(@h'
    '_g-H+PY#BaAD2I$)n4vdx3ACkFHa`5-ObzEACCKXd+@&fWxTRDSX-$q_YO{Bt<Sz&>n^zOJ@4rETJPe;FXwYUzyAGke*EUi@O*gdc1x9$?X5>oI)~?z?!o%!'
    '-^VXrSp64EJ%8?F|B?S`E`Q?R6wZG5H)gN)+TK2VXI6i{-~96AZFBZ#bAR!qy;fcKmgdg)4=<PdM{B*)#j`oQ4EJ+?YrN;5UNzg3<sZMl&+bfW=iAPwh1TM?'
    '7r#I6nw`h1PmdQ~eSG|+TD&TCpX_eWefxIzz4`8E@p|s#?Bm&UuYLLPF1z9l-c~zj*IREtfBtxRcC@tmY2SHwc>ZRRZ$Ei=QMrbJI)2n2jl15HA9f`>_qp(^'
    'U#Wc@uN6MMIDFQBvop86bk%!wx$tRm$=vns2JTv`l0E$V>8xqG3!D3UFE5YIW|v0CPhNJn{{C#a8;|y$<fr}fw01mcy?nR!<mmkU&UJQa?q>5>Gy8F|u)lh|'
    'zG_yNybr54y~UgD((TLf>dnWePhOfIK41Q5&CQl>&20Yr+~~*h+qsvE_U>_S<z&zQSi+@z^V4MY(dFvh=|XnnviRZqkD>kk<zn&e*0Y-Xy_UVIE$tpWS-qZn'
    'v+!=UcCc6It^L^h`DWC9w|a2C{P=p#St#v2dHdvjYrOem(ajE*KYUpK{&A^Q`*rAmDsR6&I-Xs7<BqPkUw2CHPFA1hJ$wIMGrxB8(%tt@9&dkpJo)|Y#yr2W'
    'f7F&f%-LJtwm17<uCK=5o@Iw0YYUgZZl86EgUzS*_3FFA;?Mq(_j38**~Lx&)a|@kU%h_3zq9WzEj=w3xAWDT^P_KTx3|l?zdM)P`}r>?mHz0_=FRu<^7-Gd'
    'KV|<u{Ix$h`LgMr9iBgXz2Sdu7JIYR@7~VY_*?V+`~J<&_~q60&4PP-`}31o`}^|q#}nt{qc>e==Y6Y_KRmVySB2kuoqYGvkNlgtvqOK*pMCW4>YH_YGx+j)'
    '=XAICZR>db*;{Yv=Je&T@^p4GdUxr*z8j1-j-IW&yvzS8UOhei?SKFF`^vo7EcLeYXKxoizI|LffA;C|mru?2i!UzTI5$6bX2<W`-*cZ%zn|PJeXx(lRp-}T'
    'ZTz#aIPA6F-ZfvlA2$w8UaStD*<eGx?rxZ!r-O~9_wUxOcQ>;OH}2%u_QKBcJE#BZxG+8&G)JTL>vikfo6CcZ?drR%<vL&dtM^NGtM|D0t#!A*_H_1%cmASv'
    'I@{U2{cTQGcZ;>{;+xV+^|O7wXZ3&Ye>f?<Hdp5I*N;B@`n5JZTrb{s_fGR?_V8lk;NbJpyPt&*<EIz)`O~f1?(SuA|8VcKTeFV7fBE~_)6wUjH`ZvW)%&v9'
    '^Saf&h3^NQH*e2(_pZ-hefaz6;9&J^@$jf(t?t-`@mkiK6urvt$(Pb?^~L6Ce|#{$+56R7IQ~@HsSckVuI!DUYz+o)SAG^hF2CMCY%Ps0+AF`aFFM`3z47ny'
    '@Mt!B>2x0N)RxazU%u@uoxJ$?{p#;*Z`R$J{rLMNd-Y^{eEH-<W%p$}W18k)|7jjqKh!EG)~(wgWzWrWy?I<LtTuPHYFqV;-5$AK-_JDaZo}w$L&G)PzTtL!'
    '{&k*%M|`8#8G7T916AhTk#pf^%{y!ZKcBp*9;wzw<3Z2K4(l2J%o{*yvpf`4GYoqeg)0gIxQ^4)z5w`>O0BkcxC>x2XLi5Sw0rJpKT|ep!?BYyGFOh%X%3x%'
    '?GA&NzSHY9dyd@+UbV)ZQ)kpX9os{E``YgL_<HDh7qOS^o_#TBA`oAD+W~k@f8@2#wU;Ajc;WVKXwCgOb~`qbRQuc=di_yzI9BhVhkyO&u~GSaR9Y;SjV@T_'
    '9b<Im<p*BRZBLB$ndi2lCLllT!>22EbOxm^9pmcE>pA(6V_z6&POp;(asn-T9e*AH*3KNGJMQ)JU3X-RhK^$Ztqi-@<H}f&Ui-$_cMPxJo4|*mKgwg<NPXkW'
    '*70HUq*gty7;SId9}(D(3u^{ay$2O1fKlEbIBge(;0AH?hS2;vcc!4qjQ|x7{uvqsx9wfDfI`G;^TaO2LbJNRLo5TMn$5i0dRICAk^ypwC$nr6az^OG@rT3h'
    'H_elyYAxaG>#gI1%JE6_VC(o@C8@yPcBQ#}T-iFHMiUAgRcg)ct=E;LPkVp=y_Ht)<e*xuz1gdzeGiC=9~bDO)|G@VN4_TYJ6t5K^Wjoy6bP4!lOggwffnHs'
    'DFg`@N}x)l7jeQQ6iA>=yi^K#;ssME6fYPfQbLh9o#KU(Nfj>_rq&V`ir^ZjRziUUYQ;;XP%B<Ag<A1~F={0giBl_HD4AOEa$#yMV<Ck?oKB%n2^7-5r_e?('
    'l0p@|NQ@q#k8w)qpOa~zmk9U1SfuX(&;$a6KPHhNR3eQCp+ae72o;JGBK$dl6rlns#0ZrMlVb%7gsa5~691k+lUSh?vc$@zP$pI`Mx1zwIDKMel1UUR7N*iF'
    'meF2?NVJylF-)I?5^>@z#0$kKlK@F4OR<pfJw%k{c!3y2c#4DzMJ7>+bhhTlwNkUT^=iKoR$0P@*X~{I)*d3{*B&C<)}~MXwfm;S+5?zj?f-xo*8U63uy!9W'
    'tUZ7i*6w44HR6Ph(>0o8%?z_%%XfyCq}=BGku!jQ?2%)Z|N4&s|G8ZQUs_g4yuklP!-@6_|7#8}Ee%jT(*@%b?XqGX?Y7XTLC>BzLolftVHngd7+L4eB-606'
    'fL_0o?e;u-lm+nh%!Sv-FJ^AR%o#DL7dBKJL5mr;f9do`-f)6HKE0`I)u56YwB=m4ox#Yc&>yH<o`%LDG#aABrd3>AB+I1ljkxeUSY_Ev$DS-_Obr+rgcci;'
    '*(R2ue{_0hM&4CFle@h$bD43!2X+})f^10U>J8HXI}`rY%cX{fKUhD_zH?<!xp^{lLSt@jSOpCW?v8UkaE3r0E5oKv2Kyr*84g%=Mg|O}Ost+Td99d<Or0ha'
    'a>YWyjDd?7Nm}uOncj+$P+IwLnRsO)e8WN`IWkhqi>oOkRayxTRTzy@QX5c3Z)E6<#>2i2mTOb@&_-M=HLFLJL$Ld;dOh>%!<XjKadqdzHpxn6%bZbMXylC4'
    'uL}kGdQ#cnkGzJdgHDL%5Ly}81BaavJTRAbZ|wM4**{gLUT9byw~ezYc$4FKW7T`E54>rTZ^L77K@X7X<kgThp@Vw|NBh==eeN{vQ<!gA(R_}@iY3HLZgy6='
    'KTJ_;zI|r<zU$9-T>G@|`6IXO*8?}i(DB=2r|Arb-Vj6xGBZmoZbzR#ZLi;TPsc<0MRQg5IxM2tPh?T+=>Rm=8UTX9FEQ2(g<nq*BBJyy$v_Zv<$C65>*OTU'
    '$dUKQhZpcD<P|*g+DudHXzRFgShJ|3OmXq}=LC>l*5KaT^Dxn18Z~hqHNCE0)7-RHimMT!dFg^cYJP-&Lya_1Ovk03SOH+Fn7J@Vw7aKf81lI9j(n>gSu4ob'
    'mm7HG-E;b5pfk+FETS<FZ(VZLm=PouxOsapaA0w%XLgQZ-E44I&p`Itoga1^i3~t;1g+)S!;VQ}gnq;7l66g%adKcIC=1dD3_y+IWRncQFN)<TALvj9L+^*v'
    '9yuK=OroaxKqzOqH9|HKk6>v;ImEIAU7tAxhr}1XDwx8J3O|stLMELcff9>v78=vrocF!qC<|+;)w3^J9oz8Ac^;*q+je|{<<*M~fHmvY)jBt2di?_tV$4}a'
    'F(kI-R2GiRd~s>fxbQk|*KM<#uWW3cT{s=%6*87ly>W)?#$ep)xox9u5A2rP10HjHqdjywK#Pvia(dnsIUIK`+|kf=jose(rsG{2Cl2T%Mh%-iCcKE5-r1+8'
    'JqLLA)a^S4%tolw8iU&6=Zvj^-9B^jrTM}<$%YSyd$s1_iFG^EZ1(L7r`en-&s>&Po1i^3k(Zi)yVIKi4sx!Yb~f|aI62z+oZkl$_kAb7*8!G>zB$9P2K#Ft'
    '`hGnc+Bm2ZpXbIoJ>;GKr91Tc7f{pJ(SzrXvu^l~V;oj%pykewu1E7<`!h2$m1_WHbQ~TA7YBvr+w+dowkJ^K!tUch!RX3XyF>3HvBl#2LTP>l;GTHnVcVfH'
    'z%k<<44*SUm>4H-wn|IOMytJQFD<UFtU296slDRZ%Zshm*22O<XW3p`S?(6#%~E@DZE>x*xYj8YyNk;U-O@s<-FBSir3D9CIK<@+a2^a1^PIt~YaAc$<_zi5'
    '#{PRf7#j5aJ1D>C9iVEsD1+L)aR+7wk>P9qYrk^1yLVV=egrdNuX<=$#te4|KAu!R9B-q>PWZ!@f7=CWa2o{K2|&C3+DA5@Azfjn%v0ue28OFM!v^OJInA3B'
    '*Xebdpx40b61=^zuS4$^;T@3$)QK4~yMrP#WSGu){Zr5FpU%jAft+Z2d+YePDjQdAmmc2s!t}Nmr?g$G9&FXB(YBY8+g?p*do|p4acbMB4yvY4YR6ljUR92d'
    'zrYub<jHLp3ki+WORe?N!&^V7>{kzC1HSqvjhFt>kl!KuZ5{3%Z0+j|xLd8BREQ955YITML<oO09Jg@}!<(7yYV~L)N5$hfE+!AeSwIO`kvaejAysyFX9E7K'
    'ej-AsrWfN)!@^zra9o*5<%@(-I1A{YHGQzR|1N0z<V~e=q<4Gi58GZ2x4kg6?N8O}{)`#~wOU(7T?l}jnvFR%H*z6X%}LhDF%@&7M>zo<{=Tjp*Y@`J{;nL)'
    'G_W1^e>4xOA1nHZA6AcRZvd+-bU0r$6-B@-kgtQc6`%nQQWnOwpx%C}h_`w9nmR`A3f9j+==pwg<o3YAA=RwuyEmZp3IH=RuVK9af!ue7`L;KNKL!;xZ1N}2'
    '&K^QS4}x*{>7)V@z2gk$Np2&EGrQM?P6e=y=g*B2e-p|>Jxhi1$dmHP%o+4H{w63FE@L)S*IYkA`!wR+6YaB00m_)ziQDXT&X};_CLYmxn@X;Ls$j1-VL5{~'
    '+e2@VGk^(m2Daii2hI?AQa0Z109k06sbkSb2qnP-GzRBxze8-kzjX+Fr+vYC@P%5^UQ_#yoB)V{_VEhzdeE_&Bac7xwzLiuv^A$a9=Vqe=t8163k>72L9jt$'
    'Az0oN23GJ5RZs)OvyfDClzyo5wmWqt@*1r37xlJrX7=2!;}7gU*-FUg`C>}dEaEUnU&68%6jb0BV>Uu~y``=*gi*vjYrqhm1hMiGo$!d-efPrdW%&;csvJcd'
    '22lv>I)A=*Anm#)z8X4G3;>I8L*X%PrwwU@(CLHOrGYGj=`f8I?5UihXgF-zm$uupTRkVK9NLC3Y)u5$Y<c~$j%Gk;w(gqJ+|1%{5G$Q)O&Y;3;3NxlN|=*e'
    '0i@s@yg^G4CThpI4rC9o4OXx$qfid;5hH`O>oW{vCOl~TiEPW6Mjb(b%xOq)@N8@tJ%=$=<%A83K7&BUI-~S%p*HNxz9pj?#u0i+UL~x?Ww6Cq@fhBrYGGn4'
    '-)<J{$4i*PQG)M@0%)5d6jaaaNd2ay{w%fEST|0G-W6E7vMW$<U_%95A%FpbQMoz;@k#U(ZPsVppcN$KhJ_HcjwKhAZim}DGc<h3rI8-m64Aee<)M>>zd16`'
    'b4K4Ps?q3Q*6}6M4xR%G9TriLE&ULfk$vu@!Rf}UZy5bJGt!)iww<@Ir2vjZDa<42)lwfrbU=MpVG6YBP1v|)V_h(!KJGbT$Lnil(h`=VCBKP=d)pmNEOb~0'
    'EORvUaFsM*B8Vya99iUR#uwn{4d5!f=XSt4c6&YN)b5Eds8)bJ0sH}mVBgE5LtdZF=y-O0x9^Yae%q0*8e&Xx?&EiU86z?O_69Jb!lzOY)IzV9HBJ1e=E*<i'
    '(-cpE-vt_WCjbtLqJxV578`10wT4or-q&Er0a=i8x^}1!JG9inmh|s+rAOd@eJIk$BHe3X+76=z50jvXplP;%bFP04%&94AC{g*tB=o`5(1;QM|9fm4c$W_P'
    '9e@W$p0QuueplHMdLz)!?)AJYrvu9zOYOGZH(<rT>O*mO$J;hKIOMiG>s|yUN2s;1AgUr4vb8I3-0K*yxYAlcqGyPKZbRo1R8k#c4MmVQaM)ez8(C7Wa>l2v'
    'TID!rIHUHw34nk*nGF#$y&D>^`-FU!hru-C9HWmk%xW}bPG-t!<*;EKOcL^h1qik71pd!*jeB+iw9<PvbbPOO=@=~s=|Iw0bc8}2=P^uhLJ@%YiQ1r0K--rP'
    'ZQPWh72J^hGxB+*`2(SS2h?&J*eiPi6aNas6rqSs1_DMNdR;6pA$HNGhz_cc%?w8ZI}kA*V~FiS-3ty*6l0A0BsxSwWZWM*cKZy~5O#!(&OF}<4Ol>H^i=D#'
    '7BeAkJ7jrIo4G%j0fdefEJXNwMw^+^Ck%{%Q=FD(Tqr~cZ4^A>hV!rxd7mQw_5aYT=Jv-<1YZxRgId%zT9F}P4l08`zR2P`wezL(E^#7KAF8|kEJ$AjX2uYv'
    'GMkAgBW$(2QbUpT73+qprSvj&BJFLz`|!UTUI2#b3$G)%qL=Qgfc}5A@Dz0!O&Z2Xz(R+86#AxREC^F6+?^zjh>PMA$LXNzc1e4h0Y~C%P$?-Sct{R&7<S;='
    'jyrVPBM<<si9tefU57S8VbMo%N?Uq3yS?%0nONrywWi@>ECqxnE0viLpBy0`2-8RKnW}95IUOR6#S|<O<ViZ=L!|cp)^;VrYyU0wcx-HuDQJ-Whl^Y}kjAuH'
    'Uf84d8U7mgy>@#%a2;9!*}R-LwuC$l4I&D8m!q<wC{~`~QZqR*xVC{i+a!cXXHc{SOKSTJS8AL^)MkV&hO93TF@PO<y?{AJUa(jU?9rLn+X)dY8xbI4!%Udg'
    ';g7Vs2U;L&1c<L0FNYtAwb=SLam1v(PD~Io#^d#+P0p%kpWp?h5(IUkNl-Ks#9-n=jtZjYap3CcZ@71!BXv7NZ%~H02Mgb+*M~uXbzBHKeH7LWujRl(jnCUc'
    '?uUotpUKI8D9r9#;-a06$c3ndW&S(J?eTDk^s;Cjj7llBB>u^QDnOd4T}WO+{|N0Qvr&VUYCb+dk4P4t(<L}t$;qPgu~7jTGZ~TCB3WQuj4|%V4|Gs`Kx37q'
    '9U7A)jNrx4`8kF)3d`Cf36Se}0FAZJK;2`l*-{d&{2+mTSo>E39X+zi0v$b>_)&-x^8eniZAgiYwIbGMN{#43PlLlQ>4N!ZD<%VACp9uxG3szi5n=bZ!S5dj'
    'GR6{=xNNfUPnGv#K+T8IxgK$mH}0vHSO;jp-WQ!CpxYx`IsLgFx$ql}SRYk+&FdXO#6ES9km$TXM|fUfqI>@%6Zr~A;$1b_&a#ZG)<~iQJ=m$yunPeJMp9_N'
    'b2`8Ti9?=XK%*2;KG7@Rz*Pf#n6z#LBcOZ18$z@u;WN|7CDxc@gdV_`Z?=v<(#BeB)RGzVVSLA2tK;<0sTu+hWBW+u2Q#98oXT1t1~u|VH(rwl{IOAGR;G%+'
    '@H2qYdNJ<7^f9!)8+I4wlM#WMOM(fj0-5~?m()-?AF0FI#LXvAncK9)*hXu7Iv<B5B=bF!P7{wH+>*bMWCZDTjG>-oL$C{~>+S`p&Y)=;0=#icg#DVqmcM2i'
    'cgD;#kXbPRG$^vFHYf-orxX|}1pmORsZb+CHf{qle9c5Yatl+z>6Di^YVQz&xsJiy=*MAe<BS~nDNxOa=|9|{l{B>@&Wl88Q3w|b+k*NG$#F{w+S<dU_OxY_'
    '_l{IteGi~2`$O0s<^Q{0OEZb93OpKMFv)<41X`qtOcnC*f4ZEr$0uZu>A@EXc3Ir6+G>yZwDi#U4in&ej{eLQ<wNPakzFuo0i>`sA4;3^QS~5YVPlIS=wxCs'
    'j{Y!sv%B;FV(;wjM#wDn#|P++kBwso9qK-B_4_#kkJG~+=VCCzEq`zD9QXCeyRhRyxx;D=pkN)4t-MbyHn77s<&<H*hs&clK5YJ^k>}Niz5Sgg#Y&a`jh3B;'
    '#jT3ipf>IvijfRs`X3`Do4I?)tPLAX516pgk$kYy-F>jaoiedyfY!ZpI@VrHSx=+Kc6EQhvR!LxGUR_w9RwMXA$qt)<AI$`s*0P3!M<~R0f@@V2M}oMxblC+'
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
    'FsN)OXbK4^gQp2xSV(gLH6A40alT5@!n{{vyZpd0NDtmsW(jI-a*H*O`dT2k5@~lAHTn|PCaH!B-25|8dexdV4X*?_CgO}A&??n3F2<m_w9qMr^+K&i#_8Y6'
    '>+*dDplB-+DJ?Mwkf|3Ma%VceFMSV<pMw<-{kot)Om`H-poV%b^^BlBJaToP9)4F&+^@l9NAdm!*o0b7imE51LZ@uwOye2q1+LSv4kR_d3C$xhv&p2dml~v)'
    'ndTp0()aqPx154DMaY2k2OS0#Kn)?G^vGxf!5?yx5Q9u(cP^-L2KI_yVyAeTKY-^28m#-#JbMo6U5xAbJB$jKzn62Vd;~jsNBa1JQdE(XNR2}C6XZA^-s2Ae'
    'BLvnHeobm97$prri9G=31E)jF_MILY+=3z`2GB^xBTF1WeaZSLjw_-|hBZ-&C9ak?HY?9oo;gEIi_nzAg+3P^8>^@vzW4z603(bsWYF_Rc@aYc+QT}EcRDsj'
    'anztk(`kDQv?D-Zh~+TshH~(rhAp;vq6a!jbB!#&YE+|$hF5^-fDov1Jn~N^6p<B7z3Dk<o6t_ntU>SeCK?e#2^CxB6B(d~dVeeuIg-4CTgPNbv5@6WLmnm('
    'VnM8q@Ie}7!GPUoIEvxxl6^=+N9j8-j91LAo`(uxc+qCql7%qSlb(M#df10eB#m!4*90hNr_?Mre&xX!4xeLGA;~tu(L>S!Xq#Q`H4~c8MGg|hDgrf$hm(B`'
    'SWr@%+rYG<gYn9SDjRitYJ_Z`a)5Xs*~++VaEqb@Jl)*|c9QRMTmhR>(iRSsnAse6Q_;z>M2_YTPL!V0k-rC^5jn$4r^)4|{l%Z-L=<a>NYjCYLuSkKP~zbf'
    'kxysdIP{Em&vq{`bWNg*!gGj`vJqmYSk6s$8N_@kq7phy<7O?sM&{2KHQQhKWy!my{Iqk#&PoR-dv8;?-lP<bYUpW<?Ttsi+i{GQVrhPUrMS8dla#hKTX>Y*'
    '7E$BUGh&ZNUcN(d5dn^Nf0E5+M;xB?l&L`xjcnru1}bIVOYDMa-iN1-l4=~evY=)Vo<U9UR0Ks;NgSJ~(W}7`RWKH`C@_tfie^Z#q?uH-9QH}GgYj7?J<MnG'
    'eB7swa^~*yPy~NiSDt1CAPb6O9fwvpI{m^np&4}@^i3fueM~@Z8Mk61((l^?5L@V>2GbljoG&SJ4cMx6OxxDbR2lXvQ!A<FqLBHQ&ajISrYhKh)~jyU$5k{i'
    'S%REb61L7I6b;P0#8pGfniLn2l}vR=u4Yr5A7K@3ge=W-OsSM9GAOE*h#pz@t^m3?kRsKr2NJar(Rn3V>P&!!QaH8K9lZcA9RGi5)#yiD$xaD)CBcT$8!u0@'
    'H!Lf#D-z?NsbFA6U{Coa$Iz+|BFtIaLu#>?1`!P@C^^oQfM^Oxn){DGZ5nZxOGw9v^c=|M4RbmH0uD}c5SkCB39+1JMFD8huf*N93o$gos78Xv>2z(>bw;ur'
    'yTHPmTy+t-SLg3|f;|lJdZPA2f|KxC7`zsl9+i>|GXjrKMmD)-;Kxd`QiFY?&{k05-i@9PAfY*NL@>n-cTelWLQZYt{?p!J{>e%00z-a<iV<iUar0g8LwanA'
    'I95QRrZgeShJ8WYp4TCSRq0^Ph_WF+qM(mHe?+m(RFHQGTek^~5T+7vijl6CH^E5iC`9x_^ehB7ljudDc2nBpB~ax#02PW?AJBK@5=QodM|!jvQz$jSp8@~i'
    'yXy(QyPn{)!WLgq`*+D6j;M%W4opE-EwyuebVhCxs4<VFLdXlEhm5Yo!3pN5IwSi4r_%kC^v^jq)`=u^H9V78Gz#PH|1XSTw`tEZnJ+*CX)0$^irku}#-wO4'
    '^etkDB`P&_&23KJ_dvG^P-8_gs+MX|+qg4m-LL)Jhd?|JCpK9&C_T5Hi&J<on6+mO=~9Zg#hTI)fxE_zkE*Tm-zRzWA_S6-L9q#}faDTHr_OjeV-5d{PbCE~'
    '`2=?iYH;*S`6%PZzCqs)j(x+AsE~|TO^U+OkI|u_piP2+4VsKs+0Z!y3V8k~S|W8LOp}w%)}*Os6WcXnr|XiJ4pELK6n0Gk#vkTgV8bQY3je@PP|2k-NC9k&'
    'O(wML@sI<)(d?<O8I~9LnxBMtKraNn6v{ox2qDI0xPDm)cIl?UcZ^n=k4BOJ|K4fgCfT0Tg@G8lr)Q(co;B$2S^6CDtXX3FE)cW)8|_I1qpt_tPRBzB0#G5_'
    '#)Hxw!by5%LwRag9wAA<-c^2EwuD8x8uY}8;YD7;%eh!$k?tdcDKUBNB$TK|wOo%Av@tdP5B9U~0IktFhECqNgRBmX2fPvVD0pWk<U2rv+qtSI%#8*$k@zJ!'
    '1~VEg8f$__UBMMU9}J9qI})M|9po8?Pm&PaPSUhgttNgn&HJ%PN}5EhmK~1!QIDz6-r-AKn*)tNeuQ9>Hk9SUf+|tj7k56xV!>?+nVID6)`CK=?B02n4&~)A'
    '-IhcY6Bv^70zQZ|GVqF43Mdth8UgGujU;Z+L*qhw8(|W$Yg2@Se5yph<L8n3PRS`F0Py_SL>8c=mf-?)zHAcogwe@r$<Y9LAPueC@idG@=|kgEVhI#gDDq4$'
    '(bto*k+oZXmXkAKzb5dP^mFmHDBc!v0T3|eDXU!edSXVzFVmcIOL9@!Nmi2^LDb7&=s_{yHRdIukMZ#G)&QQ0rPrE(s`j1dqbrY6_)ya3)|ju;8}!D$NYnw6'
    'W(dMdgno)}&Ndz`vjd6dkGmka0s)0bq-i5W`csg%Xkj3+N_;9;j7B*UDiP?2<aNMek-5d-=Rpe<5r5e%o9k4#&MGGoSpKH7Z}1x<08Dcp1JLCsHG^gJi6Er5'
    '0p&YRUj%)MQfFZA-;fs!U8dY0DI=p!z`!vnYMGIQdb%f9OkuIcHl#01(~-&B!M*)=J`Y`$RzBH3@N6JoxFn=V`e-Vtk~*`(_mtqKQcWhATf7c7g{1WrT?B~*'
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
    '0Zvo3LRhfUp$AuB<_O%=M@=C)ya@AlG+Ea!8)3&MtN6T+)f65KETwmj0u}s`dtuXMym(xKsZ9kH?bCQv(@w&feg5r2pRmYFce-p6HK;!Y9RVv-2r}UjqQ-6;'
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
    '2kAyAsR8PKA{&`DDuLw~q-tV!;)ck>upxNRjGv_m^*b0x4SHaFB~<?hx>^K2(}l4o!!-#bl!-E_giy2NnLrY>GT`rcZjcMtrz;tg6*=@gh}jS`Y{7UyOd3e$'
    'xF#IwtZ-t)i!t!P5|>be`!g{*RUjFeN%hcx#M82e%LwmsLy#_3OiErX5LmW?g_*T+BS-ci2vraQs)O!OGPh!&eY@+7)D%xb_5YNER2s}cxC=^Yh9QkYB*RaF'
    '_<pc85Ni0pm0`ryQ`$20xWg>Qig7jys1_cYP*%%KPRqY;{`H^7M&<KSzPPl=8QC~674N>?I>StcuTX0@syDd%gE`Vr3{rOToeOs~bX{Y&H@@k3mj)(mpGR<*'
    'C|xdB9pkdJqB5=dYVqsv)vc1?{+ZqJuEcd%BNZ|<kGbNHE6rNv_y7m2xwTt4tXW|F^+$jG2k&bXk3k9S+KF|07kYPG`M6j8AYOks+CARdsWd_2)ZkTMM^mEr'
    'Ou3L#(wBZnpA@Z+{JBMDKRq+%cuE&15r22k&gVx8a|;Z0csE}FBoKK#6vaatWCu&hQTEq=#HEoUdJ1To@rB<WmdPI^(G1kfwM2Fp1AeAb;X`>vY-H(qhI#2a'
    'S5}h~l8Jm|gg50P%albXGU?#SlqG6{oipWI!OZlD(vRf|x#r%%(f&LT&i7q^zTG`FxizJ=)aztL@Gf@bnpHF#5v_SjX3id1`VDF^=+GiunXEwJ33PKJ#c*I`'
    'QUzsYnhkEB=MIcHtCE?ru1NBdqP;^UQuVXmxMLXPfV09qY^p(^zDVZ?B4O$+*Cn_HQUFt;Wpbpj6VSkfDVU8^TPId@v(QLxBYr@?oM*adhx0L3v|!G97%j?R'
    'LV6amswOV#nW)HvuEf|_@wb>9p@2@A=w49Mu}2mvOYo^K8L(ll3(AJ+EC&F!Vo7?g!ks~2q7y>9qOzRH4S605WiXXJP3DaG$XY2DBcI8P#!n@IqDB)8*OGJb'
    '&_kyzG~S`>p`NQdlu3*ZFIjg4BXWXHPN&Zj5A)((cu*0gC>@xZR|soJV0oCt8FLyAOkE3CzIj^y1Wn9!{vv6^CDbArp`57$oA0>xY2WilZritR&&%vhITxOG'
    's-~3?GeR+cq#;~1*QI)4)f?-qa={bV>&gs!%IAvLSgaJ+^j<6Ab<&}M-SE%4_PS$F#M|f3ON;uKGjBW;pPrT$1DK3QU~uY4he^lj>`gPMD@2GWW>ew>(V%4Q'
    'ps-LlEMT)$txp=9_!6Mu&qBDtNaVB+QXGd~%4uJh61kyaLiT(Z11@iAmaqhotLs%YUzkXW`^Z|uNpp+BgU^u$>1^*FS$KpflxP;6a~_D;M;6OGmBkhyQU2P|'
    'WB@uA-<Iu*=<yLHwuN^a#X=$4iW%uk;{4EDgK_Q-98u-Oio-DsPDt<x%_Y-_jd)HP@8O}x!<teTCA0jIAa-(#a;8YW6p6q?C^1jq7}H$|z}#u<qDmxArBG2z'
    '1H7KZWn4i03@sBXYL_RK6#b-^Wi_KikZR28rMO{*Az|#gJ~?5+xZ%oj?t^60){Ee)S~nPs*rKV>AEb9oh$d*2>ByQ=%z<|8jbTlSDV7PV56^qL?I|m3>WRWQ'
    'g9a4Zu;gd698qIIff*3k9FdD*$6FVph`<D<pz>K!SaB4|^+3lxq}>%LzN~hEJl?Pv$*=??w-96fhzjJ3Wr8vukPuV$EPJomCbck|H&E86`;adAW+mM1%4kd;'
    'W`@Ap3Qxv}+Xv=k>geUjHd3ZJGCkr8U2D*%xTMp_A-j=D5;&R%M-~T#OKiX;S5dZFq-=xev>vui>dMe)%vr?;v@gxS)TYB)YiNy&tlf;HSe$rjH#v2ePCzrI'
    'nFp|OiuC>`6H_%Cp<dW<0~(^-U~YP3rE`TDWk1b!))v%s8Iy#IFbU%W8REC81Bf$2QAwK%F=xwvaW*9OR3Z^mT|zQBth|K9wNhU~uTvEmAx=?SFO~lVqeKTK'
    'V)+MygQOPPb&?G;wGkN~pzZ#v=zt(NK#K>EEd|;DC0Hkih`g{i7?o%rqW*_4hy4p;MHY6U@hVGmZ1=2x0+tVEK<!7C3O6Y<{;-4VfsG1~lC%h30`+MUI$Ah&'
    'im09^oGnyG3zJV4rgtOi2x?fky?Ae_Tp%3u_qoD+!3=Agk)=p2<mCif1<O#fgtz$jdPI<ml>%#~cT}|;<-~utiZl9A8TCgZpFx<h*`bT}DPnz!NRRU4U;iQf'
    'cYXwR{)GdaX@x6e3FUSz8#Z+Edc`<)Y<9_CmM|xL-XRUq8)C4F*rKvKHbn!DJOgZ7@~x6bNBBvPtJQ;aA1Qs6UQbCW%5lqH%}&P=i73Ke%)38V>7{iWM(SSS'
    'kYEYWP&U1;UN>%GgL(hRDlL>FzAJUaKk#zuC^Yq5I`vjs6FHb+sh&(NzmSFD4jk=(@cL%x0x;>h^f}Nq76uW3>pM<IK%+{O4^5Su6RqXf*22@CYHe7Bw7#?d'
    'w?n?~&^0uX^qRWyUykW09@ztE#9Pvc#}{nHZ(0jw(M%nE0xTl>;s}axG0p`fB1_+l$%e27D$L(?VoR$KMqWBbMR2H!h1cUWMrF!G8ufU(BOKUh7k`c>7KUCh'
    'IdhC_FbtZzHLv$gyffoQ1OUWAkx2~_-6`DfK=A=W77JxM6p>^CX`WqqbWisoLyKS_a|iMk{9@A0;bW}%fNdhp;rfi#%9^;SN2CRbywG=DcEDHq`H$tS4merJ'
    '3deLz$Obi8!tQ~&IUIOH+He{V{1No^!oWLO-IlnL7c;$clsGJ)z$9go%y{>(x@~waxRE1v(QuY;C<gGQLTNc)ScCu3o|@bU6C!;uZuQ)@wh{Ja?2peK<BdJB'
    '{WCY?8<R78vRZtO{`EZhpoe*C{c?de)%carx#tIbsfute&HwPRD}as@zQd+98DX?Fss?@M3isB=qcd3HI|`yd&)ap3R~tTIqA^~O04cR39aHn{vbB47spJJ^'
    '*b`|$5uWfIQ7Go<%pQg4%)xWMO0uE#WZtMsd<XWV=h*~pe{Z{Tcv6`kT@$&2{X`WHY-G0vb{ml2hhgjcj!~M&TV=0D<~mG%dEXRzTo7L0#?4HWER-|VIK?|8'
    '$v4@-J6L=NZ&e*R#$mMvEgM(1Pxn0cU}))*8enM=ON!7qozj^*piGm%p%jjfS(gJg<7=h!U>Vt*r_~oX-B9v~jx#UWWZxr>;z;&#fC^F!=<}R!tEMrh<$t(t'
    '$SX@IsU_xC5W9Q`4*KZIJzDtZ#_1zJ7oMN2tnw8`l4Cii4(4Hyju^ahgg6L!pZ6CLqPE?G7s`Mv9Zfk&^_&=l!?|hE&>{~=jq$1H6yHu;A=oq5=e-d*wi@Dm'
    'L$=p7-r1+8Jtu?F)1#qHTb@4NB|+|7Ip4ZoujgGMZ>m{9KzMdzJA4Ni?o2zw7NEspg*vmIxjrTKAQ3Xc8eIpN6@y|y@v5D97dGy`VkWze<F}!nLyhoE;}4Q~'
    'cpDZk1qYJSGyyt;;3^~62~gr5a$p-i^(L+-=SzF}nqK3~83r7a$Nz$9qj!)#VHu<rj1)**kW*!2AFoV5z|-V!Y?w#>$T$jEW^0;645S$$Tl3pzZvPzgO4p|i'
    'W|k>9K%+pC2zf_#gb-({TNHii6D_b5#Rh_T=la+@6Cn_8T-m@`G;f^H;mLBeZ)*$lt51zjZXaPD<J39g=1*w*k7XAPj??nIa~ybTYXOg_4&A}%Bfr?|7z>Ll'
    'YYWT8)dgAy&PJnwUw;1l>gsC#oVahk?Oi-?1J^zu5jjSZ8qd#lobqc6`PDqIVIF64o~e=7sqrGxvZY#9Ar#yPg|*wkEk&5QK9Ub6B}+XRlCT`i83HH@L}Hmh'
    'zAAbP*<zf$*~*uemZ`U`)fKz6;&hgai}u38LTRn#tS)tnt>xvCvs7$%7Yi$^cA>b|b)2<@6}#JZTJT@D)LkleSC>j9$tc_6{3gs5S_eexR=S=FX9A`=lk7$@'
    'n<(6UjIKk<JVy?I-T{rkx<+_c!1~A_UWcaB2-CrWB*f5ZnmJ<m1C}A?p`Yu9O{MY_QX*8grc@nZWSt(^?Ih+&Sy>k|c|bDl3~FL}SW<CGI+GN~wFxB)AtX#O'
    'C3w7G5u+K<bvPHH5LP5RscY~P84&OHLM}%g#%MWb_N9wrXh`!-$|zc$eZ>pBWRqZ^gR;1sU=D6Svb@ut+K{DOYk~lAYAQ}r1K<snNC}H$wRm<M)_q*uG^0X!'
    '5hq4+VhG9#-|+?(A{|2lbp*i$BAV7ACAxVQfoXf`4!!;bU2j#KUntG5geNsDtEZF;MzDE@am2g-rg6KmO&UyDG{{T=g%g_PrLr#x0gBKOD==j>?N8m&*|<eh'
    'p5Z-Dfpa1_9K>r`wAIwhJcl2CSVDw<0nIfyp-I_ZwU-uGSJs?vq10Y+?B&JQY73@kXW3p`S?(6#%~E@DZE>x*xYj8YyNk;U-O@s<-FBSir3FW_XD}ez#eCYJ'
    'DW<ZcymShhlNgS5gr;9HZ*(T0Si$<MDBT_RdK>`(vl^wogbUMR#ES&#KOUY=RLr-flq)*9sn*P}q_CCRgCQLGJ|HBSu??%fqb4_>_Y~*4g=UmX&_k%84Cw`B'
    '#gI1$=5d#5j2bS2>ymem7cLl0go$T1Q5C`*V0hpX)uxL<4_9$+T%R?(;sdZiNkJk_;bUA{)yfaETT_M!2I!-j+KI7xvBeoAfS3aa>w*<oN$(w$W^{^_j+(+G'
    'yKqM~Q<)*bR25>Ilphl2QV5Y=%MuYf%LEV9-T*8KVw7OEW|BAq*9R$+?}6gk!z5~Mmy#C=sCzrU96`6=aWCBtUOymIX`yNGLO8;OkR&k$`bc$)?&KV)<&#u@'
    'A@`nx^c;*w#@Lto6cQ2*1Jb$#W(K-`(d7mb*#W`q$W+jReun~@=mE<oTopQ=BV!jh;0Nl!JaXtRSy*)ms|(ks!X(Oi6Tx9grotJn(84$)jZyZ|hYrx<r&d8;'
    '7FheV1w6{$>vA#VW{OUt;9t_y++i>z!Q@fv2BHWcFvq-Nnj^`^M9{M254R6A4HRMGSF}6xY)RNHU<bLZ^}XSRjoE9-gZZKMI=}jS|1}wHJaD!MYD5u)G09R8'
    '1T#$^P)V72R`HCtC)GnvtjSYb>Y}W7>T7IZY0R^y;B}xMwevj5Nk*(27mkgVen;75y@|XZZa}w`qWA$-fXZkx1_{^vSXymvSC1=6?%0rLQHxBeXD*=@;n0-s'
    '5A=WiyRZtm6C^Qu=ss4WhvrXEPuh<P0x)G9r;5I;M`JGUb@H$qeF+bYT>9<=WYNb`srbsEr47_A5N9Kg=CD6vD_wfg6Jneb^yRkVbj@~TRRo<9_ON|cT71q$'
    '*M(Hiv+8}Y^|@I+-l-g)SVb5?(ARw5P&WXRLt2g&#Y@sj?q)OVJH0OMjhbbc^LUnbUVXw4%6PnFs-GIcs!a9_S7d^d7jwWXimc_=%w|)<S=IjQ9|XYu^&iaW'
    '-8|SkY#trMQf93bc<4Tsifd(_^f**>_it>xSTev$NC*2n+G!k-C4eVdajki@bzC{DVg8BOZ2MeXrS?zWRF6)e#3F`pj&QwNEE(6u)zh+3TorBOx`LO0v!-JA'
    'VZC>6ZtUmGvwmJEK<KGswaEi%k759C%`L7<Y*adH5sHs3z8bqdWE_>^2CWlnr`xkng^2{>vc+4Ds%OaVl@m(PC0`v^j;hDl+1m_8EW1Q2pVP-=&fFoMc&9tC'
    '<U5+=&;ylSf!@dW`?)goZaC_4L_AfeH0|jy`GTr6kXJUk{34ZAF7xPzGxkt~Unf8fT9-A%?iE47i<9pK!6V*8msJ#t*0^)(jI_vpdfUVMvx3f2EWe0$zQkea'
    'x-HE4D7L}y;vUN==8R$x@*27bxGc-GKrGF*!V%a}*qFrT(!nJ7S$@nR%PDyewlE%O4oyr}4eDIHE`pmI;SfHoSO-9}rNuJtfn?!%u4uwf3dU_j(fA1}8Tldj'
    'XbZ!ZSl}eFNI1y=kdUNms3-t+&of`}AntE2Qp6lakn*>2pD$j;Mms~IIv2dn9Dd5=GKUrT=j2o7F22-JQW4c0gA*~4#)eTW6$;cAp%)K5sb^}{gRNSX3Wvql'
    'eNEvG9(lU6nWMeG|K1{@18Bb9IzE7<pn0%${H{{V@HQb8BpgQGRUg|`T_yp;X&x7ZpL%3u|Lf2#%i!F+2)VeFUzl~psfx&%im7lgCp;bEdI)ZGsaa{!ypNI?'
    'x*Ot=`lM06rlf|M{p$9+%1(xF51}@fa?9N7>tKd0<%$LK-gcNpWmHm~uOAjkog^RR3Z`Ngz33T+Iz&r8q+|L;Bssc-gpFv1g|3y1X;~5|bxd555+aFq?Ynn1'
    'y<s*!wUu>@xsiQTV`1&3j7S|+y@Q+3JG5<TY+ZUTU}m3_U;PrD#taV^N1p$3-Nw*v(!D`t0vY7!7teTnBI&#jJcL^)hD=j5A4o@%Vs1ZCjH%u5a(Fk`COZM8'
    '*y2K|3^J<`-@v9AbbS;1)rT+5{jEd6LA)Ct+Xz?cjz+}@(6(jO`IZ%6bR{!Xf}*+rDimI`F(+QIzMIyFb`@Jx{Kl@_5}m!yO)Pl5KDy40CKi8F40nxlW^^rE'
    's?#-R8UC_?H=NO_D!SY(6UgWZ)tUsg=yJ0Rf7-x%&A1v}X%-0#=Ww<#>Sx{s-&kD^6{STdyO>)vb1-4?-^JV#JujJNE|laxxVwy!-J5g4wPktCdvBW2HpQyW'
    'Yn61wk|#d8bm@`jLBu&MhQZ+y&g2+AQF7mkw=SfG6&4+G3hi~(F+KD><xz<Q8@%r;*Veelq8}~Jo<mnxb6m1EmFFe6eVevg#Owo2ma3!Mf!%YgX+tBW<@x#2'
    'njx<F!IrLIzI#{m@dH#sB9WFE1cw8RM^<q)DefeEm`UBmikb_`H29NLOGc`sDLbg^sFRSNk4lRL&iFt`kuMt5^|22IgYAx#E-l1UM5L)xTp;bF6rvNA=%^7@'
    'Ko6!p?va59i55Y$Ezb*IDmwPy)9A{3J~|sZO1_dqTr_nGLJKfz+juR9+v^#m1V0z5s&K-LaQD>#EgOx|3%Ap!3q2KYaAGfAWCL9%KAA)yToA8?bv*M4=IU^w'
    '^(5-!KzL|gf%1y#Jp~_T<vMSN*Lg7xW}?`9vv*vXE;7xWNDE=*i^>YMJ9G$aIl>xIo?6(@klcXcBwrSSg_`Eyri7QoMJi2?r9zUZ(p<6J2(7;<-Lg49uFT#v'
    'b#aI-wjp-r&`RuyPf=Yh&+BD9a~d@xCpeWWhI1CssG;5*UqS-Z<>)0S+FTxlrj8nlc-cS_J%bykEb2hixD}#+G%&CjN-NyK=5S@LDXc5)(khr6qch5CP6Am3'
    'd8uh##mi@Ln$YY5?k?l>y8xRDbX0cBU4Z`K8*|2*(Q-yt=$<7-2ve36xNb1Jw{Q+S@<wT#VmM<;KoT2)0BCsfN2OvA0U<Jb2-8wp;S}zN_M|YKt!yd6$=AhI'
    'nW~^jGe^>-xRxswa;0LfRLYeWa-}7~0K}9VR*CCm7qCugc>{$byj`V(LoxU|v5TuYP@zSeB{NC##w(Rpaz<$t{=a6HLmgU_GNR=Tt>$oPp-GQT)W1$?7fTzk'
    'Tri><pJ93Zh*P)$`drUQ-$O&52p{)HmR@iUSKt7?#NM(>E4&{oo6!!Fr1d%(OgW*^lALL<^r{1@Q`f+<eij63@f}5hTG`0)kCO^mDM~ZU6<4P)PC?qo+KiDo'
    'nqW{?3i8YaesBI9P4qDl6F(=f*+Zi@=sz`3cqqBb2?)$ttARBgl%&oF0g2dU5srz5pSsd5lS=>@2)KZNBoZ4@PYI_K4|@+{(sB;p5-f8waJ?o8HQGW0)*hqx'
    'm*SOZw*#!cdE;2ziM^03h=ZqMA0e=0#P-6FqGK4|g-FS|PD+Pxk+j+F(RL2htvJOJffuPeMTiyNp)F2dkn@R_4c)I41Q9b?gj`36AZ+O*bS~jtNZ`*gEzO7U'
    'IHNIVEv_N1X?(l5R462|hOC`1^0V1gzl+8*jkzT=FbyfSMba`^jva)cq6xvbs6ybUzyy@Ms*oiEfXb8_=4@8k0|}^dv0?)_uUH5jwvM;MS8t{@bDP<&e#(>='
    '3x!<f<V~e=lqoOa^KP|zQpuDT3Wd9%wdoC!yh&~5)0@f`bhZevx3`XutMCk~lax--D70TY-um>aa(w&+%fX9-%6|1QQ(leZ5cR8Vh-Lxbg1%p*Ijrk3ziLu!'
    'uR5h)SE&#h)-Bs)W&AfMt_7uCi%eN6FmuIRhS)p9LOz$#rF<r|BIUHpG&7pO%VlVZ$&~5O-IVoBk6DHVbARhq^;mV2mrvzW7BSN)#dx;b=w=ZoXVS~!jGn`k'
    'uxJkj+iQYcVPmU->V!D_78-=`1_3}Ja{bw|Ct3_X%2TYNmh{bu09#?1q{RG-ufe37vq-Fmyau9B%soP*%jUi?^F>y|q1RKkKB@vyQ=csSWG4U}AW<84xHBho'
    'e9yP|a*}Yu8IfDvTnEd|l1D(qCY;=8)2?;55Vd+n{0e*nTXddC<h|{<T^WX|?SToOS|7L2+bVnTC1}uH(019@lnSvr!7fIQGNB;7gacE@OgrH%7CZi-(r}1l'
    '-;s|Zc@BQB%j<DN0y@eZ$vZeO;K6YbncY+KubTOwNx5mK9~VV>avePA;A<9$P<4>OgF+bC7h!I6Rap_QRqz#ka8|?}hsDAtlkk(&KJYpC*l~Qke#Ht<NLV95'
    'SuDuT)ah1dB&#m9c==rlx2njcD_;e3(-MuA8J_4f&)LY55}-A3+vj7ojh1jS8C@utcG;&CH$!LO&|wQYC_;`HX+%@rA`S?}s7oAx7GC-%y&XYr(inE@{4VM4'
    'V<-_~k#L`*YjXHNPbz_u5Q-5(q9$FVM|<1vJ{(1KUIDQYNyL&m0-&#Xq5L>364<{@!a+k09lrc_9Zg`CGh__&Hi?#0fu@KRz4~0+bdWbp$MzjUtR;N>RD%(d'
    'm!h&j!Anr(=4jLhpHze{Och@2^)$&K3x@(p5E(_9B+zP>--k19=%yjd-=<)x?*@kv6oSx-rK3ro&GAhO9d|b-De%A*Jkdg*%NNZJ+_x=>*tujGP)NutATiZ6'
    '?@Uz3B+I$D8X;-|!Y&6KsthL&+*#W!lmj%Pn<?Q|2%m>=GLaZL`4efx0sNi4-B<?`J49Auj~(iPo19OWD0eyqhfhG)@HEdAhL4cvJqnNmOX>WSBM#wVD4cW('
    'YmuuOd|LnKW5h;JQE4q06V-FV15fLb^=E2b|Fl&@vnqk2_pX@#pD|!CMhb(8>-6Mt!zlMCr6V-!#P>1^Sak(6&*_}ZIIX;p91JKV`<YFd6TKnk=k_pKRs`+H'
    '({}1!_(2bJB}&35PP>UAOHw7)Wi3nF(Za9MO)Yv?)Kr@+>Rp?dk0-BMPW2UvjjBznRLTc8%!fy4+OBnyii54yIpMhG*Gf~=0!tA|ueA^+J{`Wr68d)EWjU)+'
    '=MoeDMyNyY@OE~wI*Lr|_}Vnh`?@1!I(A5)p^#0Y&OfC|5K3Z(cOXIs!S4sp88bsRkPM#;jG%agsB!->eJy(K-nh`|`MG%4b4rG;(0;0(&`}R`Bhqt~h=*4#'
    'E+Ti}M#z?7ETSf=b*p_9-UAd_<$N)x{L$sxyPRea(NA5WC}T{LnPZhe{D_G%Wx<u}S<ueRhXkiI?xMyK)1c1%7r8h>Hon$ZE$bKWT3X3Do&>N+dNK@`h}rWX'
    'YfoKPtrOzC6mN*V^H_BhJ`LU~iUCw%Mt>Z@6mU{%Ak(H53i6C5i3pG@iyz9|w*FwW=3-@6a;pht*UZ#S1Vs;;*SLyL-$fTGE+5gpd5qr5&9g3Es2vvT_HI3H'
    '>8nH#GHxNBvMIzY!vDr>NU6M(OD-4Qf)TI7-q?iQ$0A05iNf`eAFnZ|Ub7dEIVN*b$pmpvNg;s|t%CD!V1D`FI`0VJqzqf(eadr^V*q5+3M%W~#71IDwiuAI'
    'bn;}Qd{@sB{Co;{b9Svfy#z*St~Jsf^U(&AvU~M{k&A){m0uwr1@)(p78Rs=odSDu*=727h5lWof7jsOMy^iN55F(d_htINOy8Hq_Z9lSLf=>D`-=FoN?%s#'
    '%PM_YH5)P!{GVc73I^{Uv>7>x=!)t<(4AzY89|9GBfg}gY(9K=xyI~LS^S+_O6;)j{9&)K57B<*V!gsr|DAp%AjK#o5j%-rri^z~NY+yX5!VORfy~Hq$m^Cg'
    '%S9v{xleL|9v~ia$w?36wpKYnCwR$HFw5K57>5*Z-n>f`Mp62v<b_1z&-ydUqywra`Z609UuD(1M;-;UQD*DLy%;lP-{pVU2~9g-5C4Eyc}iEUpfY;6DQJ(*'
    ')D&z?g&Z67h82gWe_sFhWR*4;^(3?&Po+>EY^z6Nha--oKd`U*L8r}f>Yf#qY^El`40*2slw}ptVJXjG0-!V>Vz6RbQAHr)noZay(~iQV)|Zx4G~`sN%OXgF'
    'ccenPbD-uaEXy%JA}pJFt}Yo(EbLCQ0UL8Yu<)~bF&<(rrE`V42arQ9w5t@fkc%YEEsrl{ZDrhtFaASj)cmWeQ}V9)gxGAXw`ql7r)18O?t<uEpQ1ApIKaeA'
    'tS>j{tdQNWGO^hgXf(1PvK&46loMXGa`aS_=K9wc46Q&C*DHrrIezXb$2NaCa+c|Co-c(Y)X~)uPwxdi2(vQ2iO-j~c_0ZB-fWlKdeYC93wGVg$*EoI`gM-s'
    '%ceD-%3Un6eo7L!c3`2PM9j$-f;BDuA`krnkEDR7XwYe5EYU^~K%_jZoX5UgqRmatycUl5PY&YL7+wW)C7+kncbHYOLo-UWkbNZ~#yqPJqGwt{In`P;QY%@|'
    'CZ3`LZj-fBE*42R+^d0=M?_1-S7i>q;AAfHa3r2&7iprf*6uou(ZrF-hk6(fjTtQFxvj^>Hq0V<Xq3*Ma11s(*=24O5&kKI7UqpDb#ab}1CyC>9|uSNMZOdS'
    '7&`Le)4qU8A2)RT_SoSdb-Z6rRH4jHz-)WFlxy|m&DKu!lghmsOF{hL%T@4hov2qW;q0)y&@~k15xb&5x+l}n)Z0gLZyg=&e`(hC;Nz|(PPRZVE1!=l$9o5r'
    '!<uk7CLN6rF&9OC=rP2g2a6-|;etbl!joW5F<Z-Qh4GUAy<_!q-H&zaL0QXTfOIkmzkIT5b<-*?E|vp5qqIo#4HQXK+Y)Yzh&z;~9qCV`&wu^weq?%!sGa1l'
    '2<&8<inNPL>g7OEH)Ive-elEDAM(sVG^>;sDx)dgOTx}b3OvmP0la+iqRMa@3=W3UZ3bH#3C<>}L`Z}V3D7HxKg0}FEs{^(lainVwZ}u>6MiWz90ddF#kbf('
    'prU?6!(0qB`*<RH8B-Hvc}>bj8ZODi3y1w`0gq-lK&S|iWe{N!>?n@8(2GX650S62E{WHYi6w=7M1dJ0$?f_uq4G~7*+dVLBiWdZ(*@&yOIqp8JXBCc<<bnw'
    'rJ4UzxirIaX(m}N&9GdWDc5IEF3mJ@GbER0P%h0d{bwE~mzp0JivJ*QOAsUwO58FnT?(}G?=!t{+IA~hhEL-I+06&>z@K$|E(M)DBm0l};ZJD!zh1r`YuR4b'
    'MW9IA9*ueqpWy6b##~H)Co|LJj04ZZQ#c}5aIs)g!kJexubGSXAI8b~V^9y>(U{Ze3P%Q|oyAky?uCsf28ogeX1p6>{wB;!sAoh0dW0njzuVqA!qYzdgEd1-'
    'q!ob|+&g-q)@OL#cdo=$sFAa~ytm4Gsexw(^T*4Kz4SwPO`5IoBvVG-jo88&OmB|quz2TH76&Dj?v})%@!gRl_GvHN-g%Rg6(jTrs31m<Z?c57vD1_%VzmVK'
    '7}6)v!*)6euw-rgE)uL@YJ5^j2@7Gf3pm<`NJ^1HgrJmq5EE|=^)o!|y=dEm>1UGDZcU6IMW!1YWb|*+G30f$KP~Z7rZZUAZ1><>$e>s8&m8b<)!9{~4D{KM'
    '>nLe2u^wWIMsyo7#p8QQ`Iofl;2@k6k5F)IuyoPM`z%7PFTtY}aiU5F4%HmDU?#-5Yko)dV_n7F%gcAPk1-g@%&2=614Q!aU_yk`LJY}2Ey>r9mKKw#5eXqx'
    'P2&WEv8PzlgsdAOZ6N!Q2s{>46oZFj6Zd|Fi}NIuhr|_Hw83qrM3a(CXz-qVBT`2WjhNhV?-$?NqACf`x2&cllJbc$)5SgqvGaI6KrwpjVr1w8NfJA|5gjNM'
    '39Py4LLnd1E>7SQ^7Lh$i>7;zbF*2!NZ4~M(ZF~ZA@JyyN6>G*s~{NLN}iAFUb{UW&`lXwCty{knaubZ96%RH*UNMRd~k`c&IIZ_g{6rlF;L2<ynz6;?_z&Z'
    'zY0TS%?KUaNSy-f$Zr-gTX;4g#-S4r9O;6o7PR<eX4c@73`Ew*nmkAT=aVfmo$zmL%8{(n1aE3MX7n};0bF0Sf%U1loNI{-sw@<NrcsL`vk_S{7IT6l0=5Z9'
    'qv8+gw^ecae9kT!I-)$ZK}V@}i8rhR&?R};J7RNUrqH1k&u;bnc`0T_XJu<5STnMcY+9l3p}DphajqtfHhCnnj1lN({J?xON&J)!O1i(*v}2)%Ns(0M0WsqR'
    'Vdde)_+2YfE}=7ks>IjOyy{(8!sMs)I#p~>7ua+6LKJ#p%%3d>aXPz+m{7rO$<uN=hMNT$u&a??O4rT8KNlG)LLQcY+K1yxiqMdvManA*@{bBJDdVGq9UACF'
    'xe#6T<X*(BSdhz12UbtY_^$}xlu@L2=0nDVd|Esj!OLP}3ge~_HZ%+Z3Jru=mPClkC3%03(vIZ|xqT&9yh0-<AJyiSxTjfPon!Yj^9VJi<I{`Ymn=nB;K}r2'
    'N0a3ukKvTo)Ld`td;;1^ITx*EcJM86vN<@{T(}Dq0GZ=ABq<}wz4%B;pUTF!j{jt3q+84hD?S|T*Rf1pes5?#Jv?whhwt^Uc9eFZyS+5c;(jS8H94SUQ&{k-'
    '1*J0uO*{Y=o0&9R6jO_Lw#36~_qHp|?c>VUfqZdtP_5S9>{a-;2(uM+37U4+pj2Fz7XX)J{taLwE+$ziZXa!c1*?{gm~f9M;o9mFmxC%iJ_;@>HIjky$=RT)'
    'M*LvwSD!l|4U2J5p(1?b03GBsDtxDo8VV_MGGDfi51S{oDkk`miXIk-Lq`tKE-1?!?CrlJJ!;d6e)?3c?ne$bN+^P*iDN)>SPZ=ss}CR--;aoPZe6KBq2vJ}'
    '8C%>?YvG3IaPS)jKOg6ba)P5jK?6|7E9X*{`a~1>R+{?dWD_J8*wtnEbSIDdoH)H6AL<D%c~aLJ_0%b9r=y<&!~3oJK_)QDA>#ME(R?(hC#3d<HfM+(qmckC'
    '=0lMH`e={55sa10loq~ukgwHyi0BW8Fc81#1I$@)&_9yYhn(hn!5&1IHXlMUa!DycP6*aksXZ9y<jc0zu3FF&Vxpwp1iN*Te-n?M1)NxFgxP&gOE{3C7lx>k'
    '=L`i222Cs~VhUt!M=W~hpT!R$=c~L?@6Wdkrk~=`{fh}_cp}Gklp8tWj`{l!?IfJn(P4@^XJcOI=m93>?7nv|BiO2nxnYx|^_1J(R2ziKQ9j@9IrcD1=YoTm'
    ';{n}=t)mreBWMl~49emqI}ntb<2<Ly!!$>>a$_qec2bmCg7+!Ki#^4M9rnAM;axh_d0f763#6HuqnI->*7O{wpDHb`H*E&#UPz}&R|ryKiW2s0RAVv@h;9s6'
    'UI{J&piP>c3wJbhU1PU5zUg?E8Q-W~dB(QqViXT1raL)voPoS`5chm|^G4>2;+v*|WkVUQBJ}}B76qqzMKqBJAD34-;yt|!%gvLm{YrHA2HziU)%HGCn){Wl'
    '9cx=A-}hkwYXTp3!i7#g93353PELY?U|IDhO}s}0Z`>k^1+B$*eunT#q~S#9>iPhg+CQh(t{g>A<tSJXQ;}dBS`-pZ`qJvE6absn^4fC3Y12p#|Fppn;<A_7'
    '&|Jm}60sy&C6pEkW5y!5T;w!`svW0=vjW4X@K_Y#a(kDauxi>hyHl1oEf^zuD=a1*<BbeW3y>?AnFE~p2410S#T7?cIByAH;m-gdNcm(XfXl0DfBh%Uj#iX|'
    'v_dgfB<i|tn6+nKCmR~V@W2Z3sOOKIwppg9z7`XYZ-l}ja@u%>AKj;i@qj!fDQ52+=Q_TpyP7yPt~g>D&X8MND+v<`c{*V?d+NE&_$FQ>$mVbTK`#I1<y!OX'
    '2E^T3bFWr8XukP7CEQP@+!JT6m)Dkv&F6@P7>Z_fVF)3;V{a!+nU&_7>ha#+)x*?y!jh>amxFegJV~T^cyN1ec1mEoAVFG^CLDXZLRQ{SOZSuYS<$C}QlBro'
    'L$&^*1^NOfJwmg{=r{vR6-2oE^P%J06t8Y>atfq&%)!(a-X(UgfI4&hVH>?{p(%z1Wqzov%W;@(=};2sdE4RL5f$D{+auw;Q|7%{X%mf(@O3Sk(<w!8iLev)'
    '3R$;!!}k=kqo^ECtm_CxT@M+Pf#3q9RG``taGQNM;?#lw9iu&a_RZ;_K$#hn(k17S(l`{`^FFHQGv%p5qPqSdJZP1$WMd>7X&r&~d}kz5B}W$&EwWJDbS|$r'
    '53d>WtLQAwhxmQxbVd0_DIuCL*ttux=@KqC7cwtUZP1D5;PQiG&i9wcn_-D<i$DQ=BN<v~N=XENSrW0pspH3nE`j*sSnjYclpOv12GR@`Dmoq?1Y{E2VotU<'
    'SB$!;yJNh-%i^n0MD<48lWo<x;8a1S7fBRUksAaeJQUfdA~FP%fE?Q?QJE5$Hs=JeP<Unlk>;z8ZYaBTLL(1zJfuLp*Au}b9&v45P_kZR5XE)E10j&f)3l-1'
    '<jARz_5>D|v?90(E&-icRi+pPn5&uQy0#_7@8V~0^obHB=FicDi1?FFUFCjq*72a}$SIG}B!Vi_HF|D?`uj6}Ttm!?crytEKyq44Q%yi&?b|yuxj4^Ns-%;B'
    '?q}rCNW|6vamWTH+q*$D%+ILPZ)#2Mi55-~GYbFII}#6fWo9Oo68Q-aDC*fi!`R6+C!u#%As543zT>b(s}S*1M9jf^{Tty>Ps)9y71Dh%p#5Y+AE}q;xl8EZ'
    'CGiYA8*V>57WHhV<=Ml|iF@N<ib6A&&5(9<<P3K(6I2Or@SsStZ5wQ5k;#zC!Nffv#;uaK8EVv^CP9hC8_51gbpD8sCO)&%4^V&w`oKWtX%VQ&tf=C5W6Z#u'
    'qm{v#QPfP(1kQ;Lddz!tzuzMQS$IDBc$XzPA^3LKJSZd%-_tBojrDk87ni#`*8^`zu5Y?Tb6zxLSjK73YuP=}mdN;>q1Q8}bg_sF*xSGWEw_ge3^F3NZ1l!$'
    '7aodh>&EMzbIm-7jrr&fQ%)Dm&yCmYIeh1>9%{>px4Pp#J5BUErl;I6J+EKs{-C>^=`Ql;c+I;reEzU|o&Wledx0ba0X;e+_sWXMXoEw!bwHQ+$u!LH)UtgC'
    '9!g6&BePe4CzvS(yl4(TFVa)X>3LU8>@B>?_&<lRoXWR+<{NLKn_q>Obla*b+Vf5`>ZMk)bO&!``sV<Lg=8F-;y9dvzU(9*QJgQtkdXMsuvkGXWa8-ni{(NR'
    '7Nx?&u_(+hJ{*f>#6nMb9bi%{C8ARNlR;UD4+>r{JWRl)$he4X+d69`qOp*Gh8XY|7NrDwBw(<>7*uw5_4ZSmUnu>n0h!91w1=aQL^4wpOQna8#PT1H1Z}qJ'
    '15rrfho%4iKoA+U+=)6d3J;zkK@T4?B5CA+!gqH<l+gu<&DZ<Y>M>qyDc-)>JKU`_cenNq;pOUlL3!&|@RaJn$zmHh<2q;5LVDIU6enFC<;Hd3G{WL|FX0U1'
    'G*g!A-F3W({}VoIOX9ULn_O%-qJr|yF%Zx5_%fT=u6N2%_0sS%3lh$lGg7J)3s@;qrC69!iDt}<rd>QXb{tqq$<srZt}_L&QVo|$d4D)=9(nydJARZ)QnNg2'
    'SfplbSVke{Hr7c=k)1FM*T!?B7V{j90q^Jt&jv#_Hu5O*O=EV}D1{W0Yt3c5B9G3ISAva$AdD)9URV3V4>88f%*^Yahbrp-WADwI+c>g4(f?n>`wnHcdw>!O'
    '6aelZixIR$+lrP%4@KLzn}I-sKvBdc2tZgwv2`_{{hck>$|``A?CyzpJ##IhDl7LqdDh=qME<_pgqIRd0R67=*ErhzT^qAtA_^hQMwmv^%MJW%L!Q2B@UvG9'
    '_2hydTx@h~G)V4jbOayR4oXs?K6M+Gh~K-L+OPRMZFFD)sVmQ&0|G|_{=db|(qv&`SS(wk%AR>&K;P^3M5@op?L5~>bJ~NQv=9B$I#~~P(#%~QI&41I$K+Gh'
    'U*Uv!_!$O8vG+?H$IgD55AQ&%MnqNzDZy->)4M6MoRk=<-y7qBxa-|!n6NEcj%V4Z=ecu?dJhv!V?V;Q^1adUHZ$9dVrgKIA*?(JIKCez5r)Z(pcuWm3|h`R'
    'iM(yr!|zR?>isy3bcgA>sHK%acrw9_&4yCxE`Wi?fsls={M)cx@i7bWa2)+>IIUhT>|~?VlTfbFP64Qu`?>TrSb>vFqKAjMXM>O@D(9MV;EO$vKj<|3`*8{_'
    '3M;eILQ%b#T)BGX)_YZ6@6{UhqE)kpi($Ve`{tGZ)T6&V`?WM``WhWxA9#b40sp=7P71$&E;SIOF8*;0cdq1j+H6?qFz}>&SWXsMSK$}CxUgi$OV}b{ot^Ux'
    '4(yUezd6HG_o6vW)JV4Y6?P<{TV_0AV2c|`$OnC;kImsBg>9<cz4)PaYfmF%yo@~SW#nn1qlTBWNY|p&<l<(RzXwWAg&|Mg0XKfFx(Fg&nfpX89uVhl+q7S*'
    'A7fFPL?6TbP!LF#3+yf4e=wgpoKp?W!r>a!7%*q3*~|ke!HiH04HxqP0O;Z6ZAWPrs6j=Bg=z(XK+DM#fhEfNvR>X8B&s6f>NG<JQpT3HRB|CXY9^9RtZyhQ'
    'lQ<%-uj1a-7Qa~L(8as)i{2{6L5V}*(#YtmX_qYmaVxmJ;x#E(ku}Ik=^SZa<Y4h?)y$t2>X^>~jif*qMG_MxyW+=MRF`&whT8b=*Z`i3w&oh=V;&7AoE`;^'
    'GSr8P8Qvu1RvDdQhEfg&qAa688~WK8F5^j}sw2%eeBZ}Z(Lh0NhJ!&i*5~yw`Un$+N~YOxnnkn<FtPnvMj2~K6SP3PzsiM1=YvT_3*;7D$o)hwuNuY}mW@|>'
    'CC^#=Z^d=;ivPE<6sb<CS~;qF-Fm63kEmU!5p=yy4SCdCz$aKw=@M_(^8v{1-_T(}>PLrkCkgizc~{NmhuDu>f~<!LXWSyOcT*dNZnMu)8ig&zQ5dPphF^hi'
    '^8hS9?v#mdoGlDP!f+=1@F=ptRN8sCl=&r<Lu7bL3m<Zn;hOR{Zr)OfIc!oc@1v{WE2lHYMQ45qFR2G<K@ad_w|%nMs*6zu(Z*_WK0%&&oj&|R=NRA8&$t~#'
    'Q8AU`ph%C)<&(%l*`Ku6U=<XbkPumz%`-|`;|5975@r^NzH9_omXeHpbW5VI=Q|93#x5Ah6~S8ZrcM%Lr+n$E9Vs3QvN(l^W8(kU+}mkm{vm>0m?~xU{H6|c'
    'XF3_rDIw$)`U%XZn862g$BwcIJp4F;|4XnMqp5x~M9n_@SYjAm^s(uB31S)%p@B?EO$-q#P`0<xHv5BuVZh(wi$?>bj&z0lOB)IQzMd>+G(TNb*_-E<5lIme'
    'sE@tl$tR|*lWki-{Wgd|i5Jy;ky_m?K<N*8`>J{zS6{m>jdrha2N6$#vkEd?M1_V&fkZqNgG!rF#lCo$_J|y+XHauIPn|<z%&{8+f_gog^kilflQit;{D%@9'
    'L<|rQC~4MZhU_WQALMRpe8(g0pfg27aw+Fz-uO7(Jg_wpAf}~MDW=M>TEKt~+H~@^>Ar1x2vqlDi8iEf<Zn#40dMN`EIuM<k)6#(vf0>qW_37#?8#9#mwL%M'
    '_TtEgYFR2FcuMP2D^1pXp-rr~=46@YRigj$GV1jcDllI-M}pjOUF?l=(2c?q;|L{NTPk8|cU$~j?csA@G~XraJG8{sRT|nWyu2|JBr5wBy<6m9Gt9xjIo4D@'
    'wdpL&?xt3LYUOg^ky<kJI_b_8yjU4zrQJ{VU@FZk;W;)1Tx7MPBsK0D<dw5!-tq=)TU*L=GyxXlSxG`x$K^wNPbFhfV<@?aNF!Z4CofNaLHA#{OL%k9)BpYJ'
    '*@bze+{O3XuDiIlVuC>av!ri&JL%)Jf#7e*KN~NV@C<V1b=E^e;XGR6EyGuj3LIsX6(U(`(8<t^f$B1{3qvoBcQ`zJee!n%EKQ@&N@1^@HPtiYA8ME418F~@'
    '8(H14!Fw6VCGhI73tbWledkHA$><swW+iEAgp|^`L|L;iFeNE8{#zj{P=h^L>*tz5Wx4`N2qv2GYF3AXq*%VyBDmI~3Q9M<TePgWmlyJMjUa2J$lX^jgpHj-'
    'V<2`{;fXjq#_E1cAqXM4mKYtEt<W++fe(s%+*E2RV5osg7C^i3Byk7bC$*?ab(W}tQ7Hx&q?7jC>JCt8UQN{pJCIek19j{M9Hfe7X{(^9Ft`2^Iecxo!-=lL'
    'TT-VAHOqd_QgODkR?ohXyoPdLZ`%cOcelqvS$DXw*$3?i%hXl8np&Ylyq0?ejzR(n-U?xv)m(2FL1L}i!EU=~DYk7FDt#>T{!>xNfy!kM{FpFn8e@0j`QFfb'
    '8+H#m99glOvxlII6ZUUCY2OafEZi@T*)taLS0o0=VQ;aRRjnxllBFGsSOpmuer{SWE2H<(n(j<$2_0W1a!rcfFMG2=8;ISE-Szv!Ir#*^3Oz)_0s8s(QH?d>'
    '&?^Rvp7-G_j%~LlsQUHk$-8{el{~hhqx7@W^YgRwcZ}Hh6&RiDNfmk3h6t(PJ$Zdy=@D2;T%1O|6sG8T+bG+>eeImPyPc43B&0?zzOXwcxxo6HdkQRQZcfT@'
    '9g8v?Q14?O_0gG@qO;*FKw=*c`*b*!V08NkRh+i3U|`8}vAucMKBrzOkh%_e6?#~S1*g*HTooE6TKwTiyqgS1(K*z8cZJ%Tb0Eq&{`I%k)|S?nB;+eN?q`Sq'
    '^Qk_ku*i3(s8uA5?*nnGbB0f6T*<9cuy1(n;ZSZl8W3us%jo1f92LE0t>-X0{lrObpDIj8ekbrMCX0ysmC5y?pI<Epu<jtr^wGlQ*Vh*pSNlD`(Sf>wI<GTe'
    '-maDp#l4)2Oi-@%*=zwlAF<1(e#{ZO^bOq|US$SAUBBiR3`ftMF&&9*pvtYT%2r3BvLr5PyBXxnNp}R}^>AXG9B~RP>$|ksAhsKL^Wv;;Q0#N%EgFK}62#K)'
    'l`ksFOaSMVR9S{*vq@y2Y6Et}N3DoNZ0zVIo0&RCtyaT%N(QdZ@%B!*Q53oZ7;+$ezdn2Mx6_xEmH7tuO;*src<ijo#LBVQEm$#)SPA|^|GCyt`PDc8pP{C&'
    'IbWgaW3!cPIeB9>bPXqHk=Rf8rpkXN@MkCkj8;%oEnp&oVaH)OaV!E?q#?Cz^FknsB|i$U-M)_9Qs_AX5XZ56CP#=BqhsU0=+K<Yo*Nd_srBq2prY=`6V^7^'
    'C(lYF6igpfs;#oqtRCI~2cAkUV2e9%ZMWK}N8<Q(t`(u|aepf#47?ilQRmbffmAejh%~un>arQiu%clL6uuy4t}KZEWYQf@&*CVyOvAKKa7@S5tw?7lZz@1O'
    '$*QT`0jkYr(rm@-GPfw9YH_HGD&nbZKPxpE`#_{Em2jGS%T6Srj_Tp*!q&;4oIKJVUQMKRt=`afyGeR(OsGOzanF(*B}!~idPw3#!hBLMyG-lI@5WKO+twr9'
    ')gz$QP|pjJnU-{nh9iTx#JXzDc4w_~ZMU)VK3XTLm1DqZtc<Hgsca{4$&5<$qhhwFd^_WM5x!K82;_zw2d+Y$bj$A0cd4pAILG7RV%Qs{UcTAffnt20>gA=O'
    'vYjMIT$9~ShaDiPW=YQoox1d53YELZE>=X-WBzb2dYP;m{!JZ;k4*xP_9G*fLoi9haUZ>s-lw~@-DlEqaU>v4F5PQ18tMfUsg`Jz^(`OQn(An9Ej8L3Ockz&'
    'SJg4E>e$?kvW&QF-Nl3uiIc!HXMJm}*v5|tA|eSnoCE@Gku~tH&(MtKi>h_>Z)TawTB^f557qGXlky2f<F!3|I_GL0fbdC;e^$7HJB>!dSc4cfBmP3|tw!Su'
    '_o2A?cc;LNwL?`)m`<~y-I&^~hW2EFCLL#{HhSi(_>FzHUA!L&&jwxEG`vDhjqw;h_3(7IOng~b&>&sgVVKnNJ`*F~kqoU0lhMeXW{e?-SG4VkK!q*)C~jSy'
    'oH~SaO}K3od{=2JvQ}#*73m&gxzQhA3~Z3!F-OwFZnX|W#d6{n7TvYnyQ!UaaN1p|(}^-I2H!p`K<~0q#ex`K%$=CLhLXupQhPo|@Csu67n}B{lX)7-4odA~'
    '8c@s$P>>5ifOeJ66%PJ9tyZ^_ZOZwJ|J|mfy_nQjn!B0YWgOH^#S_aPW!kQy!5KP)rtB%^H>{}#O?&{INv5hIbY((aL~4D5mHVI3v!)s?1ALM<r-QPf5Ekvw'
    'n^+<MZ0n*q)dpcw_-oYrR$DD)(?R|_O<M<i*jih0UG+GCf5b^Gd!t+Ib%I@1*aD0qOpPH(EOh5m{ZJ%ELPO|Yf(yb%=nsgY7E)^9Z4OeLiLA(|2}yuzPwJ^q'
    'u_+2}Q_Yzrda@nD$u;2>dDN`9P~Hjo5_2aKuN4h}sg~|$IetHT_=b~pjpjJI(&O@J;+FHXBpg)PEa@UonkD%fXNmiepCrZYXb__LtwHP{4_F$FH7+li1V1eX'
    '&{z3eji;~5OgtQEgR9CiN&^3@*Dt#YpW45~9|dy#J6-dp>X)y6`nn2Luk=#pA%_Ei#koUab*T_6eC^KVj%?T`hk=jHmQ{F}{#La5_9IT82Vg?oGW7vPGBsMC'
    '0`GJh{FFbl-LUP?bTS3J934CZD$%ChsUbQn`v1wH{136ZJ~t_CUX_2Trz%~n<)B3s+bmJi^$OF~MaAO7@Bx%Y@CZ6NhSinP{w6eEDp3Xwn~T^M^=?jmWPw~*'
    'c*;6WGeuK)ECO6>$Ib1KC?SaBr4qG`ZHJC)<>Fpm8yHT{n7Hz4J^>-I^-dB;1&Tx3JKp25lO2+sjGv-eC}6ncmJx7EWlQ_!IlWCX71`-)=HFJk*~^L@I&G;Y'
    '0oInz<<yY-qe$qKd8n21ksb{)pYv?8<oyS5H=2&GbH^87@sHJ4ka?*0K1+Fcb(y5P1+MJPg`C{Rk^1x~-DM{wO9M-$9qudwj;Nx?L5xE3D@xZ=gy=5NH%Cou'
    '*cCTXqSWm@W1l5d08keLLa^={3c-QSJxb6rh)6;GlxnLJdlIWPU7d8Di7XaMLuNIU8{IFz8p7GaKHgf_6QCUS+4XP@nCl&@f{y~dWuri^<xuC~KzGAFb?Im8'
    'tz@I8>>ubLu4o%21*H7-^q0yE_*nwP8jd{IZhZOTt2+d1TKPOt%emBB(nBl%RtQ|lapxxcQV?P3y8?uz>K}uy6jqqCN#dy4EW7ja{v0w*_N8ZS7IpdgK=^dD'
    'z9UnR{RAHz`gc|O`HTI`dElMZhJOXBT*KZS7`y=ORK{`)zN7W66J4VUk13f`_{NGuN?2$GcCF%G+e)SI;_UV7(-#+Adn?-elH(UmcjS&G7ydYh`snfXPFlp('
    'x2vcz>ZUa-$klP94*F&)(0dMtt)<+$=YkfXjILWlMU4fyF`OgTkyJvy4i&EzCzB*QyeO?=Vnu43bdt7>n!H%h3BF>I&je%bi3P<2t#bq_-DF2R0ZKF($LVe!'
    'Ig{HCY8nInB3?)Y$xL|*(UI;QD^oi)d7#Wc%Q3Lyt+?K77wS+;+MEZ{?t~ji(`LIci<UmymwtCUDKWYFv9ME>P5^DN`|h<tj<*wXHhu9j*KLicYD_e(xV^G>'
    'wP7d4{E|DhVbDdRv(C2ne2%P)pWYM}&9t@i+B&z2GV5_@%we(mdg08Gl>otUGAPJ?P!{(Q=S9h!&GE4;oi8J;%3LWjQgQZ5w?g!OE%XQsm|vT9^8Jvn<Je8f'
    'sc)xmBZ&Fxe|t$RGr*xIu%(WQA=f=sN<|?s7p3kOrEy8DJD@F*hb8xj0x?*b+f4Vh(Mj~*I=h*2Y4tP~df<`|$M&~gH*by~m%LKZZ}Xn$9lsn2)UCD&8fAem'
    'cd$XV6wcN-%LcE}M5UMY@R#elFCG#z)u+9a{0_xOmY&5&fGU!iEEHL)ox(u_eXXbcJmzhP{`jtm<#)dCsmRHcbwfFkse8V?+ocP)d-9XxwN1}YUY`A~98VFD'
    'Xn-h8*^D4dq>$y-O^P$G6e-V`fw$CVIcX;Vg0B#WLzK`czjfjZzrS|Fj=St*rNmq$P6@DWz3C&{YLpUk>9f|?<s@!9wwt*2Qg;{U>)h1!TB)6dp2jfSwllRZ'
    'BZCT+v%pu^^d1lUhnu#1-*8JFFLVsgeQi%?9Ng`BFK}JSIv(H{jI-Zrqw6*tzq&Bt(fv)<TRcaV6Pco>%Y{mhaR|5P@I9gXP~2lrLQT8pJI(H^x4-;)kqed3'
    'FKlma^VA8U&`*&{{eE`-Hy~4K%X#zS{OlK~M0sIUTgi5^8yi;)c(9dh$5y@?_>{)bRjEDb7;&l?<zes$x5-snUt>9EqzmR8)I}I~YW#RA2?dO>p^WR=?V-~-'
    'l)K$wB_0x$A=9|}xsKAF>+PpRrOPxQU=;<S*<p*4B;9l{Xf(8vyE*~!SBt=66T<I1hr~=Ls6|Qoy=m&#W8*5hX$E0I>Rc1<OYKuaeu)7FUuIDyg#XO#x9LW!'
    'Tn%T7n@T%SUBX5v_0F+K6~LT<#0Z7?3#A>N!H?m;2<sdEqN<UoCY5^xcgY5JX?dhHi{ucjN;1`vGpYa(#8ZZ6l2fO(X+kS7qrk=WreD_cz&OMd+IBAXzeI1@'
    '_g7Yvby*oQ%N*g!AV3*1=uk>sj!}O!AvkHF7@L-v*iF4aHs`%&E2+X*YuoX&*0z(Uq&V3P`B5xDl-?GIGkV@R>~X4wMaOeJCpOtjnBx0o`*~%8nHqHR`M3zz'
    'pkJ{0KPjvTv_A^3ET=nFhDdDj(?ed`Q|5Ia!-*bW>K)P1mhxbtM9D+)I}qV>wrW%tNYD~!(oQ;GkPs1HQ3hl4RY7KOo(V2SPTo#$)u!*n&SR0Qk5c-qt{(H@'
    '#K-bLk^?%m8D4b}mknJj-*PjT<`Xq2*Z((X@J%Qo!lz{LkkZ>rEZaFWE1O<2*Nz+fATiIOSZ(krj+27dO?dqf$KLiWaCXk`zq}iDpx-J3^R$gJ4DZPgz~D_e'
    '4-WYsPv+L;#DwEZz9uN9=ACY|LdPx1H#_Yl{8}vT(>V6i$W#}#Cfb#e-=rJ#5~!7D)|S%}xZhC~D0ch=&1D~ZBRjH0pQON%iL@7s_3|i{S`>@kusx-5`sDr5'
    '!fa4eH7*7!(s@hMrB&msxb)yyeZg0Tg(c^0?${vJl7GE=&6iWBh8<yw$nE&`vP0*p>Mi6|-kCJYL>0!{q*GUYu#s2w^iO+>8)B_wg_OpKR(pL0OLeC=ct{98'
    'D(%j8ThazSu$>pUa)m@dfn~6@aTLv@%yK#H#Pyc7%X83#8jexj-?Nl!&Evh<>Vm{;(1wY$%XR9_-MH2=$;j{^wo$RyBW58YOK1|kpH1d-^#gMnM%S|pZd+KZ'
    'BvKi^2rcp^LF|x$#@iz%o+0^?NO*brMaWZZdc#?kL<t(vuQJytBX~C|xV@}*mtMlwXe8FsB-J?K;AvtU;HCD0yn;huIdoBw7)Wq8h6mWUNf_|FJyO75dem>;'
    '2Ua7YX-LMCdnA_$jg|&WgG{ufLfs5Vs-GT`oR3;S;bu{yPh`W#HVQ6u;;H!fr_isO?P>Jj`<Z@vFkYs9uo>5JjN}10pjvCIq(P)`=^7L-*b?6H_(4hi%%ZC!'
    '&rCX|*QM!C>Ay9s;+cdy1{ib#U4&0?jZ*wity-lCNoW#SjpSYLaT4gU+7a59OLwH++}wF)&gC=Y$yAeZqKl~+sWqYLL=`At+@1g7vj5NLPY+*sf7PluW?M%^'
    'q(WdsV%dJVQbI^nu|UQ&HAFuTlpZ?5^Hr_Obl$GkNo88cZIu8gjQ`no;^gV1sv0ia`>x{-ox$U@<%jGeY9{I&Qv4iR$T1gqp6%PRTG!uDhs-bNnEBDNe?Ui%'
    's&%Z1KA}ILH2vF>f1ym9Xovnx-`;i?)Rhb(k=6xR0U3=i&aFoLiK^awKu>l%<}-S**9j>PBqwyC<J=<yE{lP~0t$wJX+39BFHI;a6@;QP$#2Orz$@Jo_8k5%'
    '5d%f~`AeeAt0Z}HUg^~FHWSY$70|(%r)}qrA`f6!7rBN<YoSzq%xqRWr(wdYSk{rvZIo<w*w5t&(}u#rDy$E+qEUbD4PM`8?yM`bw0--OSg+%dK#Kx4vFl<p'
    '4Bux#<M44xRpjlQBEMkOhignBg{Ku6S_{7?+j4H=j8BN}j%^FOL7rhyW*iL9&Kh<$LHsWFKRjF=3)8<NcWrUH4cxxiClFyLy@7WwjDap-#FC+VZi0s&$Y{h>'
    'Dg@z5-d^M|r}?CZ%59G!C9%D3Z}8u+cY!V;tJQ481quNft#b0ToB7Z=bcZUY=%Nk5#jH$!g^Gm_NB)3|w;9cW=fmKCUH=epK-V7c?$ib5fy3dsQe-ZIiz-nN'
    '3G!13aXhL01!8fori)*rr~NL)f895>q7w>Gx7-pdNo+AAWe<-CSp$vJMNFsKOrFy_DQiV7rx&79JSA8~>J)8zv{-YJRP$k|muu1dK-i!Ezd)8$ImUUykwVXN'
    'kvme_38gpK1xYK}(%1#f7U>p_($@Y{u?h~qE<XJ+G5jkc_-Rmn4(8ynC_s9iUUq-Oapk;B(Xy5lc%b6Dj*^p4q^jty_kgpHQCJA`23@Bt?~=Ki5<VYN@^{Q@'
    '!DjZm<s2dL?|M3O^rr1Y$&1xWn)@1eWty}9a$r{wB7@j6qoa@^$0Y$0Q;)sKf1F2t4S+#}12=*VPwpx8FBBE<m&8Qv+CCO`C)y5dH=<DD_tJNDQ(LA{0|T24'
    '{uh5y6ih&6{)gF{xeXwj4Zd@F8FK0gk5Jj*iY$q0yOI$CZeVRwBnpF(a)*?XrTZam$Y1>l2sn*HxRoRUY?%zRe(1oV@)n%0$i-Z+z*a8imY1GAA4wxYHYQ)h'
    'ublm%zfkreIXN6bvl;!OFlA8HB)BrD(P9+H>9BvhoNDbAA3-eHU(V=w^4_UX3xs=&z97%_h!fT7)$#%3O&3ToX|)tqq@UNkm`C!!77Avoode}B%wg?l{@Q*='
    'Ox9?B#o~aQXP^;xal&oYQonMM8({_HR!Ci}mCm7D7Q8h6p6Zk9lgW19(nvc7`^c)i)Y_IS=h@w?W(pFbJEK;3vy<s^D#Lb%QrFWGn@e(@$T3aKAx+E??ap@h'
    'yZ=3bp?9gYtqD*XZ-y;3dy;zKx<k^p?P8b&3kD%XqH4o7NjBuRriC0A^JgAwhm<l2%w}WAtVy31vq0Jv+5S+btVSbU(W;`FUDB%I*Lrq!B+=pOuUXyZeJ(^('
    'B_S%477sNirrq?|`?K&ECC(^29R#{z6dU6zO0(BF^x3zs_09U)*c^$(@x5^J;W%rB<m94ptY9C%i9qs(FFqcvx714a6xgIG5}knZK|i;Y3i?@Y$7&2jSM>K~'
    'P+fs9Lh2VGaUjq|Tg6n;c3z>R>+*iOM=1Z8&xQlo<t!bk9}jgBdCzHUr8C~Q${qjbr;88iaf7byvF%@2us;prt2co;*S-)QPN_#@0r9i^8T~%ded(0Sc{5TM'
    '9^=iJcPsQ-eT;LVaITEB%!vVkzc7p(GyF0|+PSE=Tukm@dHQIwKs%@MGW;E8`scG>1E9>#OUtj&(&eLbQr5i(RucL!x5MBcYoHb+m%p~Qze`(NYs%t(A=4{}'
    '2g?!jzmjZJ<C{O1$q?~!GRQ`4oH$^taMI?Obp-*^Hw$EMts)S{Gk%&-hdV_DjHQ^l;O*Pf^X}Vsmld4Bai(&5R7?CI6W2-+KQ_u8ov;cc+&c<gkpd)a??_@i'
    'RV#TG-Qplg^2M=%ti=^wB8F!t<sZ~6KCq6{6^DbRpKpbjk-v<T7sWEEDUVGQSe6Y`7Lr@2Di;&t`K9S#h;~VUVMzE0k4!_8>MUVs(GIAo-BrdL>47f8E-wPC'
    'wY@1M^rR0&7ZpfAu8BHp-`7Rz#)@z(+&2-dXmFfP4I5%SH5KCs52(5cuUnBoHHJlzC=U9>3Om;_&IiH79n*ysUI^neg*szhOC9FIF#XilQTq5Oc7f6G12YsU'
    '`Dun~CqgsOw(#htXM?t)=l0}kG<?r2$YC@AS~62qM<sRK)T*$-fc#0&ixaltWPo{8NzSIEjw&<S)q^74IC*u+S1`SKm=mZz%hmbl8p$<Rof>_RaNF-Frp?eU'
    '<%(m6;l!>}S-mXV&lH7tYZrZ3Jdm-3m%{9ld^oF0BD;79cu8cRC`01=6vfplP+bosWThH_V}Fu-(qL7y?c>>24`Jh4vb*&Zwkvcrq#|I<lA~s$Ey|ZrEDwC!'
    'i9MTVe$YH;^%P1U(s`3mAN(D>a?!C&u2%`&(NQ~2Z=IuI>C5%=V>{-g)V!THqN5;2$|gGmCE$ZxYbJZm1D|WWUSck$HGPjg^<T$vKXz`VORl%{%Cn1jS6<jr'
    'X@y$EV6V`0*jk`M1x^qU+e6C<YM!Jqb1v-BI6Q}EAJOQnwu;Gzomzt)TU{qg$2zMIOmGtA+`6!@>gjhH_2((XUuwnPhATBa0*)BIrsGce5SSJVunSX3VRh#b'
    '`||_m2L$0g(Rrmjy&h_XW*KQS)0TKwqj{r&M(a{J=RAkYtIo4`oT^s+j7eWj3N>;}fEvP>*gri)7V$K=G%n!r@NMX+rix)AswUE-qdw7mGLc;Qp)m<8$FNY7'
    '(MOKx7L6zM!6+Y@jrdMbx!Nmh7ZsLDw`w7rekDYWjsy${b1O9vt0EV*$i_K817lP|e8EW5MiN{a=Xq%6-4EU5YX2ALP1LFsNXcI4by0BU>do#bGIDDpK~P?4'
    'O9CrhQb#Z2Z>>VzOmQq_psCf05Avo4YCc;`CL<t(ca)H7n$7N(94-mW^c=MjTV4AhDKNIWuTOqBJ9qNjjCxm-nXP2x2MiZZDM4xP@zeRVcW>zs`JtWFhM$1Q'
    '*4lM`?K!{pom9clEq;ZJ(EIV79Cf8OGt$R5kD?Sax)KapyGd&=X|Xk3v@ge$l%<;U0&w|3ETe<3KQ;G5Vb_0&UUH6mNunC{B+om^7Il!JGDp;sC5i5biyKUM'
    'e+Q=+9xunnb0%73y*tMxAWd6)22xH}mhTPY0#Jeot4+oW)?)UMHOo&6G_?R+hxzEZuhP!wI63ZMPG8|>R|$n!1;eYjw##8Yz)HU<3b8T;+#svfVUc*E4BV}i'
    '^kUsa5JieNYx<2)V%J~eRAi19BoO9tF+_G*NS7={J_gIotP{?~ZF$1+@Hn-5*yh<$-^nMEzzzhWDb6fSWK!Lw|L)O$_i<{IDl85DI=}#Kc(zN=cIekG{dW(a'
    '#i27G!$b(4000kSn<cu$Zb1p9lDwHv+|VTojp)jQd~Iv1?xe;ceVrzM6!q*=@G6hkMQ}lqoeOE9&>3_*!+QQToK|@n6Vrgt(>j3W^gY3#Lly9^jyB;JP4glb'
    'bfW5ExJ>+}hZSAvDth?&6@JJ=POelRDR_b^ZnisdVZF3BG4cgV)|(w0dRILn{9W5)ocCnxrxAq7Q(H?nPz{sBn4&-^0tAiZaQ9f(lDmhIGEm*|QK}cbExSPb'
    '2%1s}PL=#=t&o?8h(FKMafAsrU(xhPSvT;G^`+4Nd1{I$LVaX^nC+?m(*F5GE3CUXwZ_k=D4M(Qv+g~PeRn<d?Qe{uei%x`gAp+hB0l5O&ONcfM2z_0j%TIl'
    'V14o8?9C6a-k!b;Fph4ed8V<XmRzsHm>q!{$bu2zKmBs+n%xez+R-56kbD$x`w`wr5p5%Jtr8tEs`!=Z4fPG#IOmhKsrbNEQJ8Dyq4?(9OF?}9e;Nnl<tx=Z'
    'NkPoG^L7PW6O12UFXzS|!q9XJ7#i9qwdNnr(pW(?Yw$L5K7E0u)=IdXPPbZe?&O3#(L-$A3@(OMF>{SZ;)L{tU2^kxPC=DXLj2ffH&ukXROkxQXmYEZSNR9o'
    'ylf@=dOocI&Nqzy<1<3@B~bZA`uWpCd!a*n8G22IVe4Ua6l<EA8Tvw37~Dl{J2NxKP$H@xKfN%99E&4hKIEOdrO6>i=V*Q;r=9$8w57C|MMtUDstu1N+i3tC'
    'TkoHm@=O!owBv)Fb|ChEk-WcE<hrz3|4_I68*R2Nt$wIg>7|})6$PuHzguz5<VhobEuRG~t_{7)dAm`5mS;ub_+;EF84SbI8s9<wJ=S;t^gX#%a=5(gr~Eon'
    'XO1u!8OL1PY2;DQ&55bee=ylrXo2XkDH8RWgHqbG=S;9t`$M7vs@en$^d(kjvzC6a4kyCn%@_6ot)=u&-Y!)z*0w)8={OKnpF99>%g&F`)3!N*NE|81##ioB'
    'Fn?OLdRDi5ZLP<N{k(3xQ<FN9yV$ut9JZa|0#>{8YSgtg%927|8nSPvkL`~Jg;_3<)wQj2n{?0j8ZKTM{0?|D!Ba^TNbras77zBFBktVE<oX(jlTprLIDxol'
    'td1$LeKt^U{5Zc2{31RIK^jb^VuhCNol@D$_EzUmKQdMt^~jG1nQC7U8W!)?v<Nd(*W#!Bo309S$ho|l#&XTnke5+S3B!gqwE!V^obbh0Q90rBs@0kdA}T+Q'
    ')KQ?ku0&In^ONzcvT9rHb-&WbN*FjaCp|s_K;!E^$${V52u+;Dn$?^7nxU?gm4YieE?*7D6H}i!j1i<WCJv;*l#4lc%Vs0rdb6=s3-6b`S>Eop&NpnYGI6xh'
    'aJ|`Zh?IKn5EAygq(k4<K@kNI1z`ohas=13>j_C83i3Tzl?MFE6CE`{uB@{Ono`>YN%JK*c}ik0n)bAjl+SL?ncFFD8Ef3FV;N$c7mkN{NyXZ*Q@$g$-7)X`'
    'ZK%02Us!+*I^NQY&(lOYnT!UheCU)}_C|JmQCSLkC!ddZV(U<Uyw)MKLDL<2%bi)P5;rtl96!{Naq7v%=3Kg%WRe=hI!&ZxDFh2CK3QlY@(-4AIyTx4+~Wej'
    'TNM4852p<0x<K_MR>$R$vd+6kc~}W$vp^;Y5klAvl(T?7b<v%^K*bu1P!fC4VGhQe=$C{`2%q{&>1+<t1Z>zzE~b6f)oeA~2IL+wL5xpI<A*8_YXbOI+sX6)'
    're0yoV{O?puULoH)sekY2xjL<`WNu)T6fP%4Rxq34;!Dq*^x=pVdv!7g?}HVz9ec#eRFc}oV&2P&m~Qsy44FZfH@(FzG#|b_Ear4ccI!Ta8fItFgsYy+<Sq&'
    'qz|`A9_Z3O>>5mT92*wh)ucaOm(G`)F&3bAi(Gi_m8?<g3;iyN#&0=XnCp*sW}ukmX`%J(dYq4U&e3<hcEWOrV;P|TpE1S&OJGa^dfWwo-8o07yaHd>zODjs'
    '@1RRzFB6LbW9Em&4MB|r;#E*MD9X-eAG@P;OM9Rr8q1m*$D;e_@M<z%&h0!)jCQb->?V83ehz}#v%PvmU_Jbk$K#&pr0ikz5e8!kAU_`x;z_y&7>ZXRP72#r'
    'so2qg$m0G{I;b`4)Z9_pWGv2snG(E75mRN$Gb&PbYSBpLBd?V<D=k)YS&*2;z?CvRiT>_VJ?hkWEU;E}g;M!gC`_wX7x}VbkT1Wv`GJ{q@>fdNP%t{?i7oeJ'
    '(+n`w;c?n}1`?=+I#{zB0(yc0A8T6YTFu>d2u2@-{3wHsI=LJ6Bg_-%#dg%u4-tI`kszWE@L!@A`~yQVI2A`bdbh~X%lLJcML(k|D%yBGnGK>hle<ZDPUD(y'
    'B+)zgD!aSNX3bVKANQufR&apb{!SMYdPb=b33+mU;XYx)2+wrz9Xw<%6dtn53Z5|WlP8MC!E+oP(X!~t!FLpG*U-^+jz?It00*al=UyK=k0HrRfOOOzd<2>f'
    '))^O3V~zZ0tfj7@G<g=XihkQDJHgd0xMoy1eQFUX%PPw~DT;A3STQ*RE0_7s$uMiD-qYs40CA`Lq>KOU_7-k(gq+nhAN{k&1*6i$nwX`Z&d%PQQbNDqb*}DU'
    'BEV}0W6PwDl?=<)B?f)W`b*ko=u|i$5&65c5w7)dg13pPI0{$D`3iYd?aJv-KgrnIl{c?m|4k235*dEE<Xcqc#Wr>`qX5T#pOc@`Z_<g&>^gY02=hr~w|Wgi'
    '6-5wgpxL;#6F+NiwswwF=cSG%2u}<y5j4NsC4HwRJ-K}l_}b5?rB03B^M;dRc2d(k%%hHa_1odp136@GA^QBud2OGZRx9ATPXt-wJeVf0fou9Lh$#h3rC#{d'
    'A*mKPISV$XeDr$#n@o@~=h*`K-Gd=iD?){(`>f?K5f504I-yiU+m6Qhq1V5?@4?+T%NS#*kMY=2Q*@2!>UEaD>Nb)Q`THUpLLl6mPSzlbID@%=w%00-JKJmS'
    '1Lug$qYqZ_sB9OxI5XBXJOQQWDVZ>yrqI`275nunn5uOUs#ank#ko9ZxJ)p8DbHAqJD{J}(1B7qXj>X_16}gmtGFl?g+4&^4wK5AJeC+#4)2C1BGmaZl&kpT'
    '`q$F&g|9ZO$Xso!lz><!ukR|5s~)X*<3gl-i`P-UNzmLk&^bEmr<A}-ttQRHd5m6r_6^t`1sS+`gzbEuj#AZXRGW$jt*jKR$I!Pt((UJG&jjx*w<(fm&#Lx2'
    'ugme5V$Cqt?k#$5zVPh&$f|KZuS9b@u@BKD=l?lKI1o4P)O5wMCoQOXvt@?0?x{l2VYd{ggDFm0AZhA~kP`9p_&7C*74r~_--(slkT&@&3<S0=-XE90fs4vo'
    'h?VxxIT~@w39sCDg~T?1YG;ezDR!xj?bLJJg{|VFNKGjJ6mW!9=_;MUQ!5?q2kdZZl2+2Pw;mRh&~{a-?orW@(Hh~9TC9Ggp7kps!t$n8Ez189C}Fztb@0LT'
    'GAQk=VXD(c;;o(YL|JK-LdDDYxB?-oJZjU)!i5Jt9J=}4pBK96>_MyRTAyRWJ1y-?IHuG6^!&p6)F#Dc>U$R>DNS2j-zdbiK-?-=Xfg_zZA4_TsHkHY$Zb7i'
    '7|;jx>4pJa``S9gy|#i;W(R$Yi^M4d2^jYznz@i?QSe!V;k*z1Krolt18Woe4224f@6w*=zBqaD^Qo_#^TlL=zkR|r%h8Vew$VW$VBrd2a;$p<vK);j_Zs%='
    'eeX`^5|rGc-%NQoxtqX3-xGX!^N__)7Ov#YF$QObKs{`!R24RNm}Ru~Cbu1ML{BftA-{9T5Pk^%zA^|AS7UA`XH*>E4Wrzu%=O!Aij+!%l%ZhWA*`w6d-7^6'
    ';u9pqyu;{P8o`pV3qRE&e^Zjq2vaurYM#T%RB1_aX>PPvVOiooKel5swPRC7QB?Ia{1s*XlaP&2{-cr6f)>HLFn0K4Zer*PI!t>_I#>HTQ@iCg38EV5W~m!?'
    '6UU7;`cW?e&lk9RV9uLu+WF+)fmsR5dh+u8?3YSlLhL5(K!wtIetq)d^ed-XX4x6>BPTx2pCRLeyDA~1+RXF;aqr|{Tbdkloq!w@Q9~hz)oE$`O)%uiix*}}'
    's2(;P-z|rnUP4bgsYy6To5Q_yIaEmQtN=x(Djs2~J7}Y_7HUJCLnc<Xc{CZ19&okC4AFxfLAaSg)*sH1OYHYB&hA=ZFYox;-S7VL^U1qY+mg25{rT+t)j!VO'
    'x)0gyxcl<t?_^F>YWN5)1=toz#G3f1x}QWX{3*KlsJfd(Tb%n^U+4vD_sGhODQH8mFOdfuL6d$j!s>nc4#AU^;X>uwU@Lm;-n&pOGA*^Jsmw}<LYK|qxh`^?'
    'N~N5iRz0rs(>VI8)yY%=5{Whg>f!U{*-_**V&i5!4V5Hv+=H#PQ4U<HbNT#C&`bmQm{%(E1Mn`r@hvb|u<ql@xGv~=xD5sr9j{c_uz%91iQm3J(+;t_A2Yqd'
    'P@;e%G9O-zvgidcm{BHpQP`me)ISrGoDDYJp34?;l-n0%Rho0FutR}@LJv=Vyf{7AvrU;ERbM%^1y8=}g<ava_W(=-Ri$AuoN*?Y4X1y@IWZ>vJ}@RWPY08?'
    'X`{*kj|qH#B<t<L!pX}cvoqR0z>*Y!%~!SeiFy%7&!3yUQbUFJGyOZ<+Hur6$fd=jHFLeE)jp`vYd&j4IH2SzdeYi$V>JlqrSTFO-;0a{_Y=H{fP#T^4eMtz'
    'ZO?{x2-F30f3<udYH|=V!XJ1hcX{&e6cZnNoc@8MmwBSOXZ_rBhe2}>e;>B__?)#h6l<9T0(KYo=r3wYua-c2asNG_oWXEw^FBz{%MqLcR{PUYM_s|@Duh5s'
    'Pq}>%e`CAN*BN4pl6@Be0TwW{G>cC_2V6fvwF~FkDg%XEyOVYz3+5NBO~Tv)f8@Xg=SwL7pmPPXhlzhkXl6GJO_t}dgutu-g`3}G*)-xjJ_yyYDd<6}s#yjc'
    '0_uy9suB#MCzHcLPLTP0KfD@_(7zN{R0G!mX?Z`{bY1)wllw7RIhJF_@kM7~v@Q!HR{8tM`P=Thi!<QuVmHO7nz>y<$@ol(q6;>=+T=Q+^l{p3eetj=WKJDY'
    '0#s`}oZqYqshxA=QThXPkP9XnVl>=<PF~J}Q=<i0*;)s(k|k2vQO6A*&oB<7dFzxmy%8p)xyu+gfhqc8*28<^d2e<#gumg2pQA7G7+Id>SX=-+An)*bSgSYx'
    'w_tXEL*(nHV^*up<^orHmJ|=Y+IO7MXM)ZCxf@kX6r}7&WTDAN*Fro@Chi2N#SOq;bHq4pkMD~1a6l0faIR;PdB{u%x~S!Y6=e{0oDQ41;_q6jzI1x29v-Qx'
    '^5$or4J&_dv2iD7uy-sy2;$Z1=zici{6{vM0JD%y=W^LIhsv_=e54_+EzAR44J$&<9aX5ixdUghTfomK`iFNx7x}eZ0N<+e+Poya`_^!q2RnZV$fj?zIq((d'
    'MN^aFP7BXM?$w%jn*WzrX0##1zc`;@0x8^6mi^<vwSNT5ImVBJV&lib*Bd_$9&7yAYEl-F1*%injUigjkxRN}KzfxTPOyj3K?`No<(QGQutaZu10w8z1UEwH'
    'RI;>@!w|@IIYTf35}fvO`9<K76@yQ|U!S~lBk~WlLp<5xtGH<rm#|v_`1m$H1Wpk1YacSstewn)G-`>~`K@zRtd6)JTcP%2>t+}i2iJQcTZ}lJ6olC$XkuA>'
    'eEkED^pZx`v9tX?EgIkLPhqHid9P|8XdS#x>G)1W?ZNj6b=_I-0rVO#ovL8_2)8jFzP|~9F3_Lx;Rs<;)LJ9cip4#TuTuE&b^)4)k4GL5rasun3NSH?-fhN='
    'z<O{6>q8-6&EbU8$M~u}(isKPk(ZUB_MvXRcGdw)IxBFs90=sAchpt`DlwK3ho2M$iRkngn2`rWzeP4CkaWUM(@;DJ@e6x*3fB*iBJvH5E^ac^ys4xb@KHlm'
    '2C^Juu0-z<hmBmgpkgiwqGR7u5k|`?R!;dhP^N^9$dEotw<sR^pQr77NY1nj3uoG?x1duN$XYo2#+LvJ2v2q1V~m~$=})Rm5P3So770eLF=0Ej4lyr}1B77A'
    'K1dfp3V5kL-qv%RPl*AtpwE}0n>+Wa**Ub&1wU+c0=PfAT}7Rw=?~9rZ}mW8as8nXGX0&_@NYF5;%2{%e~Dgyr_uPby3%)OinFQ|^sS}^ztw`jRY=?p)_-w+'
    '^7{{`=jVUNa`52I>Fcw%mG-{do=R#6RUf4ez>ygA)dfruN^n#6(J(_fW8emcI}62J>%7jFD5|ZUe5*WKJ{%dez0Dehquqm@5c9si+rY|XAgnkk%Lu|Ha<MsI'
    'mkvaoNOYe-m(&#<Y_05It7C!Dh_)q=z{AnDOlKMLU}?kgiL`0}5uw@8Ru!$|AWBmp$0oTP5k~)E*K8eS68B(2)nt^<savYhZ9%k!V)^XP+mA=TnV0HfU3QC`'
    'tI|;7wwhRZsy0nrbBei{W%(0lvJ2bJL-fR7r*yM&atLr8$K8}&&mwH>X$gi2gM8ou>>PeGm6x3Eu&(P5#uNQRm0F=hY|7_|?cyHDYVz!^H)V9q#7#5|k^%Cg'
    'spY=+7*J8o&*r?IM54v4DlV^E%vP*+WXL%de3kQpl_Ty^!8A}eZyG|&Rt@PeEKUq$JCT&9Y_hw7UBEvQIpglZ$2Z}_%Q40*iYEFe$uZqDFRXeBPjy<o+9-#o'
    'sSUXCdFl#6Uc;_LWNaEvg`RfxI4v4gsaH7g9x%lidg3V!4^`?$D@qml5plDx_F*lC11p|D%QlwSx5kv2daUhD6Bd}K;_0E*d)FDJxUOOcSTdrC`5@Zk4}4mz'
    'Mb%K1tp9>fKOCjbLfHbACo<COJl3VG0FQxYA;FF*G3MvV2yYx?xMJG}F@j{--*k;6>X;9ZQKoK^!d6Q~(peCIM7IOuI)q)$fdUbF?9x2ZU)OMtM|Zu4=n6xk'
    '7VNSy*!1)##>B-Wn0H7_A$VRC-jFr~y%$A*(ztsD%Di;rPml`WFby6Oc2DnpW+iB<hxUFxB3XUuLx*xG2e!!zOX{LV;Cm<+lE~m|f4r^EVg8XqRK$o5)fcN3'
    '!gEQw1>?^528vOP41VT~9psC^jI;w?g1#s(B%Jx~H=1?im(^_B4Cb5z3#gXrFl@lljS_h)N_Zy0tEqz?LgSKbYC|6y+26OiH@JP>P1`9obB405$r-UQdJ5N{'
    'jbi>w%$h1Q77)C3zcCx7`eA}~LfuSMb-DDEA!ZTHJ8Q6trJKaLPSy4dZIUCpmCCu-FhFFeQ#v@^Ws-Hbz7d;D8-)0V6%|S;Nr;vQpDg}D+pc({gr=@udf&%R'
    'R_&wK{{D)-X1y8C_1Zn<^53eTp%xe<GT)<MS-d5?V$)z0!^iifxO%uW%}~oj{nTc2NLHA5)XQr!nIBiw^UV#LdrvcLt_+PkEDf!5*#`Q?a#my8kco}ckCgnG'
    'H=OQyMz_$uO5qj`ZXxqRFTQ!?92WnvSJoo}`4?V!hyI$!0Z`H;Ot-B5<gL89X<H*c?>{B0V#11opMlGLF_|ykz;1=-PO?Qu8M=0k#Q=4)jJ<n~vDYo&T6y=1'
    't-O0*Z{^)v+scb}-uk!uA6EDAAbN53>-nqGbIgQ8@)ll#cf;i!`_?Jf+PmR^1qyNp%|JvMlFvT5bD<M10&QW9=ac388<0!38-GQlE-Zr3O_ezu@LBKvDnqOQ'
    '7HRH=qg&E`gGhuGjw2O}ACZCutCQdXY66|3=ZEww8w0(Ehd`C*6gq%{&4fDy+b?=XO!G5(z=CLkwaq8W%XN4)LNSbb2xnnB84ddnG%%?TzeGMWx|_@htv^By'
    'KKd3ytG#=y?S|Mh^gdqPXV6WGGHbCKSAUK^-!ORT1oi;Mz>gW$$?_lO5y9%HuiO}XK!&TR$KwV9G=!B|++e&!go5x0W@ZxI_sDM&JrvP|wp>i=I3;Q=enbmC'
    '_3F2SuB>zS$Mdr{-Jjt{g4isuG&1Xi7V&_+QXAm?WHOjzJE#fxi_Dx(U!XLi5!wIP;~iCeL{cJj&55e`Up8=D&$6to))#AoGr?(=7G~9YJY6x2Yjg|iFp+75'
    '3fPr&P#2Yu#Ae{~)55ALmpu%1vC$Blo}iO+Mv-(_gnjoVbYGmFzVW%TX8YB}=^Jz@uWlG4(nb<(AUYKOi?C4i8!bv3vGc87DU63`{lEWD*LrvI;>GDZsu+V^'
    'fbJruB>xM)cjPx|8tu<sy?l*<H6}Lb^9HUN_TVkhpr7%NcW1xyAE$7iP#;hEUkn}F_~O>6Jm{@9v}--t@%ym-VDF;W5=Em&>Vdi+^#ki#(`K-b2VM0V_XO$-'
    '{ZQLaN%R1X!5d*-;K2f)a50AvS1&JlRGm)rOohQLK1KEDQykSIcuQlo-{Q-~C(pV`MR}f_njWC=gVe<HX}`v|oSPvuJ`7u~;(1JH?<S-u)n<o;_@e|#pc?qb'
    '#>Ve3Cv|vDr(S@ZNHq@^{9u&X$D917>B>i8b^*j|PH#Z^yk77b-h>*pe4*V;u`?YTwpbovPA|pBc{{9~(~BAG-hewb#+}f}C;-JqRi{;)A_x)rSw}}CD-#r;'
    'o7DmT$0t5j@c|pGzu#cn0&jCzjao#ht)vXyGaJhMkV7<s+Bm%nPXhFToEf+qoFGMzpQZi~HlG9eyw;=zCyuu>MsE$r)jTOkB1?teYey<+CG0s4ti^4qQdi2u'
    'rZ(H-;lg;fvh(JgB>I5%IZ=g<M!LcmF@_}Jde&*z@)Yq%0z2PFtFf)zQK|v^Ht_d`S|kx9tk?WxqvMLm7%I2d)VP<?U!&GGtY3)A=69{F9l$#-<vN}}k1RX7'
    'xZ`X<0oX|2QS_dp9KWPj9ggdBUr-txdZjk9<Qs&g2$|f2nIg!x!Jkc3!b0v65rhqmz8Ernmk*lgM;iR_Qmo_Bh>mrHLkC~bijXC7qvQGsXp0Y?RLk6^jw^zu'
    ')zq6@T0=RoI`Or!52{AROaRSpSZ_BxuL5kG>433C1_=iDhO^;WCTr(Amx%Z+)lxhqiu^o_s&42$oDnOkS)&zYM0{}5J;NPai<D)NwhZk=y?vBb;0&W}Es{TP'
    'M*`hZ*N{=nS+maxDHoCLqD+?-r{14s_bMC{{-kisTBJ}~g(8Q>?o)Tw|AdH^rrn0vtKk~H%^U>@{eUMPWU9U%J+-n%7ieRzU8Gdy%taJKZ;K#Zx84VC8J3Em'
    'm$z-AJs)Eck)w~|QOFJ1`SmD$YmO;Yu{2P_ab#!wBc!ralAYl!W9M>u6fMJtA?&!H9zl?pOkn0z;tQ%e;QJUxi(n2TeInly$PBSG_(*Ga!k!*kKv)i;Lv5}U'
    'xK+x&3cs;^A2BJ%tzK?8d@7J+IJQmC?x5&@o!Y*X7CHel0bDvN1C=I_{wx>5sLI&%hhjnqvKA>27rBA++W=2UfZ1SvAu!!VGkV!6pU&c?(x%gB%;2IJtyk=D'
    'tEm8c)gb{?PmD!2Y9J>w4xrDfp34I}`<<dB28h;!m@T~qCCEi28YlWj4CwmyO7s)CsZ4(eZ8plo&5~1-4Abg|NT}+fn#4h9_YE$lD6q9l*vV2|i&CsZ7i8aD'
    'h=Em_PiAmYRL#`Of;k-K?Z<Xhm*}s)*i~;o(g+(d29d*$W+woz>3yS?6j;WnwKfURX7n^-Ti_%F%4dKD@tka+fpLQ#aj+Pk(k&^{q$1cE7^Y|Z(-3^prfmZZ'
    ';G{^g%T`CYQ|pPhbKRxh<bWn!J}xXcM4#scij)OqwOLW{6Jc@<?qYk5dM|ml616XUbl5TqN^%iX(6JxPV>TkeP~e{hno?J%;K%Sk2|`e?K|R4j8!U_jk>uYw'
    '!p9tsrPaNH1a3a^A4)~YwsBpKjNsO%IA)^4R2mLj^Ggmfj=(+It5!y-t)HZcQIZPxS#Ch(<3^SQr{^IHQ?%N|B&+WUg{B5eI9wg;RkAgCV7c4fBl!VEy*Eln'
    'W1qvb*r3N7f27Wy9Mu`>j#$0fWP#i;EKYBLN^OD)GRku<5nW9tw}?<O7m}~^#23Q)M;P)3HO}Sx$=Im)$=M+4KlDeam6i$#067Ag9|ed(Z#a5LSTT;+;0x5}'
    'Vmx=Nj(W+tsORr{Qzr(MWfim!2=W9TK3Iy)C^{hv09Kv}aF&et0a3^2(Kb79sorcQG_LQP4b-D!9C<cy+QsS!l8EL2lY-c@!y0!OUvD-iZk;B%dwz29>MZ(1'
    'CAkk=kQal&T&5YW!nN2nm={nwfBg406JtSi^?>FBR-j{zH}FSB3qxw?->CuArH`QB*Zu&|)ozNbGaO|`ZGJPs$rzDd9Jmgw$8?{p$qL4S2k^%zyzSXaqt<4_'
    'e*ELB^LG~rk%Y3O^9GHU@&ZNNqK>E0w)5E!XJ>D8W80fMBmh&yBH43@*08!C;VG1B9lW_h`_#fdEAMBM`*FT*-7xmIYmLxVZ`0oC;^Hs~mEQ!w>OCw{aMRl-'
    'X~Duusr5KNQIzELCV#e~<ZJlcpo+lK$x$+sjo5*F!d014tSeK^!7$TCD3oz<OCZ(SPNJ*j!aDXuA<>P}BX8SI_39-V5ru$4srnWZGCcPmhx4J{f!4(p(w*hi'
    'n-=5VMF|fkuIp;hw355)=*&D!%<eFWN}(mN_Bh1C_fgAvx$*nS#p(G*XKkjvi~E@MdRX;kci72u*~n|~s<DEpJ5@SW5WBb5Z;Lo89==p}*_{HLPyaMJ`IKoE'
    '<bQXOM2z^4)VwQu36rJ4_Cra6DZz%;;HV;2ax`F_>jyCvm%isp(<LU{GK)aRQ6o4)SrwQtT<wjYPY{vkVj}>{8Ip8!+@Vd!fHz{|1SGP*%vfN}m6927ONt~e'
    'd=#CLE@EE@wNftM8+b>_YHkowm(kWDbd;iWk@=U}wNqE)XmgeHO=Ldxg-W$RT-9?%)lYJzRC@;pS`P^qF&;s#7v#gxh2!9vMENpuaZrjLsEss;1=pG;SX2@>'
    'Na)Hu;yrX^H>IyljVa1=e^k_zL!@2^?L##%rA-80379eRDnL?~_4+q$il5b2sAfUNlV~)7O*W&8b8bO~0B^FKIuqjF;dQH{R^lUab3&suB`aD*{oq2wm`eB)'
    '>TB-UQLG=x?2DRa>IpBnRR4UfT>yJ>C-xl6u~s;kT5%8(sRNOFq?xlE`^b<^O?8SB2;i1$`4m@#bL9&ht~9}Z`t-Cw?^XTUO$NPmGP`JdEffnJ9Xd7ks4OOF'
    'o}(7{P>~Dg9M_3nH1i>OI(m>N9RtH?X5?#oR{nGD*wDQi7=zj}WJ9*6t>CU8O_m;dpnzRR-I0RxyM_dRW|!z*c<h}*3~)}`w$by4Vsjy0qX5qim^mw#m0ag!'
    '!MOCeiJXnqJ81bS&uapmvx~9f)+z)#I9WO2-)=UwOu<vCor}L-Nu7k$bA@W_#L?VY?6w*mGfqTKKqzr;o_8Miebf7hxyLkUKY7Fn+e{3%_#YCQ@cmfH>WKQe'
    '=|!NS-NelXBl#90Hyuolv{?0IqY<l>6>CBhTu!iaJ4aNfA^Jm;g?&BNZLPdlN|_tHFv9mmK$&Yk<xbR9C)T+*91SgzD=9<_j;%X0TUcYMIui7Msxp^)_w97K'
    'RNYsrave5YX>y;YbXZ%LYcJE+sB*Pp<0~||K~nhDdR)8Kf1eun=hO3-ZQz)O^UQX?0OD3}Hlp`gh6igd7^=wiU<MH55k2eOlO|KCaZd<od4PVq@Zkt`oUJH('
    '|9&oR#N;B~i@x7!kizkhHK#~)sR3f=qiqlfCL`nTyTu60>f2U>KSt+a=nlLlFK#Z|a?3V%8%DFKb<B9>zzt3morjoxf)yJ*06%q`!GPw30?Qcc^9UID;b@Q$'
    '8gT?nJ=R6&>4~UEaR|6EM<c{NGnsc1rHWzQGu=%}>pGuieeyzID93B|3g($pSViS(>dh$n9cD^&;JxUfHzU<6kXD4Eo{(CWMoGlmc)arm)8W7V)dSfSU-f5M'
    '?+*T+-%Tcqn;|LNr}INvg!k|H7j=fZN|OeyUx-A8*Xd0*8$jPU`d1Lg$;H!Lt<*Q~b`^j02h7y@Ug1DnJJC3M+xIi9-JHGYF{l|=5(;9*y1CX#{~;=7JTBcg'
    'uikdiX&M!?u#pXCf!kJ8^EksOvhu3azqrHQO3(v4R|zdpQ6+f%tUBP9KK<#Z?z^AQetE};^+v}?2MWJyqn422uuv}zJk&$<!^z)H&;Jer#1H4czJ2j?_uVgN'
    '7X|fpU!47}ko57m6;zoYneNt>>XY;Nh`^ammwtKmkAIxN4t(|EwEN=x^yCfv{qD`#*~QPVPWkSp+C}W7%Zxym;5O4P?9f&GNuKRr%tw}oIMw0m&vD~+<v6Ar'
    'Pz^npW%sk;f?}Td0cVk?IBxwYtWBqP{Tn>U4q!W-ArbsAiUSqmE<*H1=P~MYIG9~kDPh2owtIuu7N^5n+zsX+sR(^zIE$*Ohehwe-a^W;VNk0#bTxVDJEz>>'
    'wGmFyKSOc;-j-z*)jXVr&>(5IQ0H)<de7)5YUl8SuNpiZ07W{btTz&~-B-_tgk1#Y1K)(^19!E<0O$Rfamzi)d?TTtX^EjDFJtjpf%l3dRk|nbhztb=D2282'
    'TqcSO&0UTAYH6K9;xFT`;ffOO+C~6j+s|HjshbarxWs?T5IW*X=pWfU7i<v@kXbE~A#AK&C-hK-F{o=k&Ci}2%Fa*Aoxs$snnpf3yp-?%lT2s4J{Fd^qcL-L'
    'Mqdzi#82vnUthg`3Fi)uuJ5u)MN|ps{Kc<8j@DT&MbL9ByY^J-TicM@5lVw-Kez)a*OX`$`r@x8+cMWnQpw1oJh^xL5J4<ceGZHDNvm~9xx<tT_>lHoO|Sk;'
    '#*;*-l5im(T>Wv8Is#~_C=!*X+Ol~qy0*=0(dAvoOt@IRxZ5-bvo7tim8yC%y|G(3eKYH>_Jj3cuY!{^`8R02bSKsfL3v6n2Y*6~6bR%f2;$(NT+&KluuJ=E'
    '6k|f>9;p{Ihh;6*m^5PVVkKbsv&GPgU5d=DdNC)uB2fd?oV+V645hxVOWe18Xnrnj8+!DZ3UqP>?4du4K^>jh&jB@^{@BUKTu#CagUm#%Ecdd_(En$u;;?Vu'
    'Oc95beXSbKnsB9r`zDghx+*zqv7V@qvssxHI=8^?`bvG9RpY-;+eTTM@fsCV+7R;=X>}2*MII(gpbu;UHwHJYU;CY-s?f=f(5(krNkyUaN(bdud({KtV?h&O'
    '{<mzFDZLY^#29vfe1b@GMt+*q%5@LlkYC&PJ3A5Okb8)l+gKy|IifouJZSBa!sQIn0mM-g1A?{lCPg<5=VI%J3y~Zo+fX{>U71mY7^%j#IsTPhq4cN*;y*fP'
    'N6hGcI37&yaRB|^6hDo2(R)(?3*bnwGM@CgJv&58;fpIwM6j4}cd%RRe>zk49_|<(d$RBSMPk<IG1By^8VAgfeuzMyIw_#(d~E*4Nypm67wgb03Drky(tD3c'
    'eWEneptx*-ilQIQSl~T*gepZLnyaWTEf6ry1@AzOnn3Z_J;Y&6G>idr7U-%<W9=_w576T8CdPHu-e|aK^crh#P|B9~$GLstp#tfjbxp>ZLRp$(Q|RO;%B@#z'
    'Ce}m8FLawPCVJs&i6~(`V!RFs!H0%jqyWNqwlw|~j+C68n|*4$?yB1d!;2e@6_VpBM)Cg-nl1C^d@LJX60}T(1B`WS@!nRjy33bZStzK9a2(KI>@!IU*2fTp'
    '(j1GqC|Wx_csrkO(Lzsv%07R|$L1|_?kP_PPbf%a=qVR;wuFrWZx5O8%VkI6AjcB?w{-mt)eUaeg<%TV)xxBJHvz*>&#3NZQfEt?hI9B1M#ZkMD+OBvRU(1P'
    '6tQSI(4kv@8o6$(51mUd_!Il$$nFe=W2ASL(|6+*E@qM5*`vsNFFvgtooq<?Y7rfkx9r!da~eC|uZVajp{EZ0$4#wUmphvih-|FYsFSjIgOY#rmw0Tu%du3q'
    'fw`Z_X_(;E-7gFm03X0#%2l_?Vwwxx5bgzetfXrH*{(^v&9K4hQ)0};F~#H)VMTTLn7IF|yC;SE;REDSzmH^As<;(t;nk^GH#*sb*<M<Qx#K$b4e<a=F>1GN'
    'iw&wt%2&@liOYj^m1JVE2A3N)Q{adu|2d((1)?_%<C}=yfuwVavGGM&Z~l}RyNb2SiK15Lzrr^}acRD1$a-EO`F-%U5~@|>zfVFv`{nfQtG7S3$uVPoQzwXB'
    'T+Vt!#h}c3gG|YzrwqtOAPU4+ObCt+^SWsfYDUSBFys@z(0p*C9sTg@-=pSMLjP{T!lUvD{)kMWW}6?XQW#`a9fK@Y+lejEHQ3+F@tj>h8ubHipTg|^&-c3+'
    'O+#7b<|7n@G3CJUZh40?BDJyAinV))=_^W<bN-Ix9zwhmC^}-JaHQn2uvGpgNb*2PrGBBrhS}A*kO=I9<=s>!WoXAWj?fLU3irb%4RU)6P2V`|RwH_j)$xxO'
    'l1-i~RRCo37$wAvSvj1sXi1&|-|y|P9Db;<3+qimGZfVV=4w**Kbphq-f)y~NMJTYA0A47dyNVMEYE`eJld)6D?wA^DLzo7qpA%nf<8<@(%P@Lnvq0wS^;lc'
    'u%7i+<92hizPoc9Yve`@{_InP`+^sdwussqJ9^C;QI#22-U}pSlLHBh`8*Rb`WPVkA6%>7H<QLrLu7WDD78q4cE6io&YfA-#~}>#y0K)=xQN-J_pt>N|K@+a'
    ';V9JyTr_kX(olY|uSP;k$Y<#J$Ajl|B8GRH(}!5&1b*M*@KBbH-F>Heg^z#R+JFAr)&U<agkXj9|A)xXa_qbBE>3@G5Tsv`kAJIyz<%1IqaHU2=g+F?;^dc8'
    's;IE0<`&gd@OCTQ4m`$b3@{+oK&MJu;4lkYZkJVmwCJu)+d!{MulhCQ$h?65r@(A|O$a2D6!>(qo|m$+ta|H0s~0<H7|QG2NWG+9s7{F4!BR;S0=T9g5d-e+'
    'NXnnpDVhotoh{chMd9yzbIlSir$F<v-rXV77Shg*w4_cTp+yrhQL96}>#WWES(d?Ses%oA+i~m&0u4y0AK1B4o>0~EP1r(*VRLK#3ZBh6p^s<Via4<qY?l51'
    '{s@-q{N%-HJG$0j#-psxp-l{v4R`qPU#R<K1wQd1xH(l;Tym&{%{Wk(=r4kui`rNOQbQI7?^4(-|7W)$7?l`wK3XnxXg@ojq7?wOzOdF2FePLm=-rA_rST!9'
    'e!^8LILvc{d`zv0W9YO;nFb|HYc5{1q{(8F1Nm|Gpy^Mf&R@<b7biTrAw@Vk1!CHuY$iq2OkBb7;hT98VbS_xQpbPUM4)V}4r1{*L(JYD@F|$X6Pmd1JrI&|'
    'owKwt9B_X^?5ySs1m>7|H{^!!0MB}Tm;GhN11&13kDD&9M#DZ#!D+95Lj!V_E&GJp0`0}xBQp&1#Z-jMbeGeP1rqmA!QXZB8-LcQ_g!?r=C}AuzLgq<H|bp='
    '4l?%P`z8iBPG(~NkuHqUxfmG81!en@CSr6g7B6p_8=44SY~$U_AQ1NoJ)69Z+0;!_Mk{KJOOy!Dfl8*WD>}>`y@!>?)I-<w?R1uX98Q*V+=|SX^8O&T36((P'
    'C3{~{g}qtkOgWv6C^{QwdI#~26t`*_O<OO7Dh0CjsCPH5j!;=JCy!O!@GvViI<(z4C+9!CdYkZ%m#06T{QCMLQLp|hmI_JXw_rGp(eQd9r-@DnbZ@U!r(Hs6'
    'uOxG9b=q5?kGDQpG)VP@O&zW{K6aL&J8i~XXExIeHSnLUwiy0~?4~V)gK6Jx$b^cx)|8&Wh4UUSXuS8>QE!_iq&GtnarF$3dV>L}mElGl>5RI@hBS335n*s6'
    'nW^_Dcf70MD9woksZizt5bYc68)F_!M);^doFfAgMJE<(y!(8cM=Jo`1cyG)7G!oK*==vDz86(%TaEpgKq#aAMs!Cbh~9(PH9vG%Z8bkzt>?`a*DNH4E8DK`'
    'Vr4t~cr;!zS(2@L1+8YYcC@`spCWa_xkZvhPWbq*$b}j$9@^`n9j|@`%Z8l2$R7B??oPeA!?U=(k5yKClw^2;2FPs~4Vz>a6RfehU2pB`k&p<Q^?OSU+t6!0'
    '?a3h3ksw%jI8{Oomn4~6<j~N<YfcY&!|?M+))}}PBdzNohcY(=EsV1f&c|{roRZiyhXW3r8&5F8q`K4EZ2c8vs9G!8JJ{o8Y3}Xwf<zxdxNL3iOM!#d0m^%{'
    'AjB3bgEf;_*h?AF8>AQ{tM1nu_P)Pr%h52WMXbaGvN6}fWb>fKs^tCHmQh>#`}`Q1XR?LX-#RT84^oMS`egpIJKNgr%4Ys2jB0^!9WVvqW2)5-5<4Nd@RXAP'
    '!<{jlfOG?+9;cHg`Fp?KY+5ArE~{fFk@N|uy&f)Fe#lWk-QmNT+~N|_*fT^DHUqXI$qmqAdp8^mxK3);&7^=D5RH~Zd9jJ)FQ>FiW*Ncl1LGkFj)>b_ZBw<7'
    'q*uaeruk^YQrAJSuQj*#VwCjiE&S26{%*vF>^STkTslZtC(#6To`ft2kr+~lwvID_ZA$<GY@EN(V1nQPxAyDX(9F)xZVY=7Ym_J3ja}$P>!7{`KU#Y&>{7Gd'
    'B!X~&W%bYP1EdeXWV1TL)~OR{>pmC(DifAdpHbOSN{^w<>$xpUyS24XT9g(a96D<QOiAAFjSS9}-mSC`9iqyu{UNFZ`!Ymeq;2yQE=7E@Z$H5sRFVs*hd-VC'
    'VxmTrNwde7JDD@*6PPeo<v4tTVgqn9Q!)t6QkcqrfA#hy1+;86OyztHPOcTZ(woukOEzpL>Zr$x8pRp%p;J|xL<>5|b%S$wlX&YUU!Y_Q;u7m8W03p?7*L=q'
    '{Va(465Y{;R^(Hbkz;gFHbD{iUe#&(po*%xtoV>zg>ILzdMo||OLJg{uFQ+UXcy<3F#SEf=)O4lk*ia4rYm$qI11|1rGGp*e{*{N4tLbwPI)-KCrHt9U>y=3'
    'gzIQU3(>N=ejvi7Q<Bj}LOdb;fxJwSKZs`4s}w!LZi-e8g<nY|!}v7{Pl=RSRa1G&`O=32KEpeN5}WY$|0mY;Po3Pwq)(v8Oz!d~>aTCJhk4c6sK&ikDGdG^'
    'ZTl7*3Y+0Bapa7TUx2u*BIKLxO1dH}o<vpOdZ>_I38@;t4%_Ti5gbQ>nVw`HM(M4g&$;NDs8TXLH6`h<Kgw2cm?bT`Ej1k_3TNW6S6e8C_zQE4BV(9)%YLDm'
    'Z`R}3^a*GYuWdviiiq&%`Re@>>-?u#adcmE!vrkf4N3nY*wJoVan7kjJej>N5m>tGl0aB9Pl32K9?ay#eH=A%YpgX~4%oY^fb<RaFbB#z-%A!TSuWgFqVp;S'
    'NYeM3fGL>LbLM|3n<(85DCB68&))8eVZUMZi`aNTnuOCiBP)hk9K50wVm|z-G@7fl%91SpBaRmT)n2;aX&msp#`!-`)%?^{4mM`K=j*Otsks!2=h9o5G>)xI'
    'oH<mgMhZ<ZkFAu%LJ%CP>8BvZ4;{CA4G?~m=D_0e9t{+~Y^i#L%G9N1Ymkcm*u+Q`qgYa>b=RwWLa1D=mA&z<JXj5L+2!%*)$q}KG%)za%I2(ii&C<=@Dms#'
    'otvAGPE`*M70He5&m@9Q$p=SHdD;5HT+X7Zl9cc!h6(4NmvtazN0G&_u67;5vyXH_aHl_2&4Yy7<5W5JXmblfghnrgQruIK|Ij!J?Atesqrl3-aTLJO(Okmc'
    'u51A>h~l=XsrADxtZ7$%D(kX-B@q>_VIy!4nMIo08^Nd~@v64usf4zYCw3+FW;6FVPe|<TFC=T-pZ{S^YbnzxJz395#w8|ZnsUU%>Ihk2)IPLu@EwDawc{Ua'
    'O)7{-Q*qOFJesQ3o-*XbQ^%8a4MS-j_3Lq5Q^_r){-^eaaC*innnarUgMm};*l^m2*=*oE3OV~hnM-_+d&4j9W)m>{jeR=VaoD=d+AK;r)FXJa7nu5yN0Upp'
    'yef4wqp*pWWE=ZmTqoUR?dUUJJ8f&e^tEQ@OFt^)6uuO<!~95_J(-=Z7r{crU%u^ma~A5YWxrn2SIuhZ-{-4_o%rRy+C+%!ln}P(sDLPGGP{AXr3$5N6{CW;'
    'JX$~(*}%r2m#nS=z+p^Xlk00MldECa+Q1QvCil^+2EAt777i!+NV-$hM<!x~gF+kxMc;@%ovli!+mckJ)OWlVc`a^49c`4aq(QuAHYO3_FsJGjMK3`$T}=>P'
    'bvS@GWTVrbXV_A`u8b2J)=AA#Z#09(A58C^Xs$U=?RB>3-%zjbGf^*V3y?A^FyOq-QmZt~tag*d$i@hZj`ojf@4?Fs@Fwfcml#`RD}F6QL`xYW=8i3gRljJQ'
    'qChK}buze+IgOVXt`r6S#Ir{0O<`APEXCXcmY3W2&Bk86+1f&tFTzVf!@R(#w8vV%KiIEB8GMi6Qwb~aq2NKixphE~TMc-82YngC-^~_3+Y!H4iQ4#ndyA`R'
    'G_;>1uL3rwLcw5@%#D7C<``2UkUP%zTl-S8!eNWP-`S=|TRRCa%w3OS_*y&k7<-FYPv7rwpLQCtIT;uwMj=EDNVRY_F6l|t#L*F;M7o#-)bzO)iLzHLIpUiq'
    'CYpuvZwS~I<e=D=jjC&Di3JX731@QIzp+vlkU~$JeZ^J;lKmKu!ac<y@(Ck53qq@3p@C^MGGyWOBkI=SELA@qJl~4j%BB&r9`cUc+JVJJOF^q4rpN7lv4^nb'
    '(RLA4#!OWBA#hi;-6Xr^E`H30`g{v$z1<;e#P;?<d?;suSCx(f8{~Emp5qp+*0z$J{oPo%xx1^MZ|!cw_u|bVUv0_TR?>pEc4zggX0pHEf)5>A+!Xh^wg5&|'
    'v`ykx>JP3sE5%I{81?3Ey+ITl9Yvdst>^IH?I!%UwYC5Je$W(S^B-ZC_~pO4Kb*WH4X<d2+YufRr6F#^(itsrJHjJjYl_<uj9zQ+@!Ll5mM2YmJKAX|H8p%l'
    'b&<{-zC#jVhgrb;2Ik*0{nVBbO#L8o!t@jD_$kKLDrGc3oZr&kP_hU<kzjB6X$dD?)5Po36NJWkA(|MHyt^Yx2;ghVpbmUdg(BAmW9TFB$%$d46P5Um89p>J'
    'cjrs3@zkJJ_}M1^63BCAc5qpS26o+Dv)nY3{=p>iQfdeHtIMG!0O?u%;;6Z#^?+Qa=bM=+nb#r@e{W`=Hdms&`?OH8pgP)&S;Fo#n++!evX4DOP4M+*|N1>J'
    'j(C;gOOAaq1B9B6BSO(Wd2vB5f~3%c$A9&!l)#)KTR=dSN9~ISkN#2WGeXQz!GF+LNA<-{pUjchCWcIvRe@wq;>&yxq?Wt5wH0#LQ)Di2PW8nt6(6W%B0KQO'
    'l8bVZn8>lhRKY-~oi)VAwK^X)zvOk7fe~276?N{c4^;1r<?{)OJ%fU;_q$U|qNkAbn0c^!6(bhN(g!=p?0RT|sTLK?;TZ+v_XuqZYv}d{tZme?KequLNbELx'
    'pSm2^fQq`iZ1z4&DKywu`CY-x-P*|yW#~#-n_|u8y*l!j8}J{H#pZLZ<V}Mw{rr<oZ6zd&FNa)sTA+n?sCR>9*43J<@u!8Wb_8PQD<1RriD-DOi{wv;HS;G#'
    'Yw;d`XBN98`?IiG8C5317p`G>XxV2KAK2D$(!gDCgrKBO6?%fdz7)#!e)Ioc$^NI4i_^A|I8jz-M;0<|!sBO_K=3T8;-l>bdoUscUx#w{z1ctuF`jc4OWSzq'
    ')LkDBj-Sd24^kadiRkKqy#up5kWP3DusHmlQd}$d8|sY~ln&W_g#{@rIQKo&n1i3RqaItwCEm=a6-cULl>=!rP_kl4U*UM<<S25CbVaE_c7^V&gZJ#jsKq8d'
    'w`|uZgC@Fdvfw0BN5U0VDuiQ5q80jxp_k$i4&->@3r}ryoQ=+bFM4yzf)vL*{c*fL?w>!0+y8ogpZXf&_;Hg2cz$`z%VCmd>Q@1NpPDck<?ORyvHRB3r$j;F'
    '-HQHcN2$Vs+dbG_g=x7C)U9ah!V-dB=|{>4`a4HTu-3wr6QmEtw}3sx&g`vYkuOdG^LVp4A)5Y6RJF>iQfl$fDCakFY`X_L+5v=&30&Fc$KGg}!3{t-CDH&f'
    '=-u<Jz3$Iv=db>8_V!&tD@oLfE$0GkO}0q+=CEO3Rw2G5(X-X)E+~Z&w2K8gsJo@$X#2!XyPzSA{b`^-VfQgCCWut$z+wM-?(RM;NOJCQ{INP@T!p@p4G`jw'
    'Ht~w|cPuDdfFN=CbgeLLVRf+=?iUa`5}dD`VD8E)`S3oOFcaOUf-&tVKV`;{dUY}hRd+6@QsHtiC~I6^-G^niBqwckOwcoEIDQYjwA#+ByPV8rCFqMFjbFPn'
    'c(>w)Rc#U%4A&!`PbZ5I(poCanS{Q9@TRCFJhF5wzWB7-52W|8Hyrh@2noiLV)F(u58s14C-k?_3p=UIF{UwH*|fzA%`JB}<!jhAgbM!Bgo^2rNRt+U;?NtO'
    '9Ghlk<AH0xRYH!7c7)28#I%bJaNYo1MTe@z%ZiBTOE?x=Pf<j{>@q<L=6T=c_N2+*rErT`rqss^dlLdm^2ArK4d;j#B$qP{6{%&CB9x{;<3{0wfUh}a%IbE?'
    'P;1tLi1n2dbTsaOYhB0|)O%gq*j1<NOa`b^YF8v0U?+5Z)O=I@ff=$7hVpT=s^;%P)_Zdx>!}pWwdx$))yu>B9bA?VoMSGDJ}?BY>0?f*vm&LSHRr)Zf^td&'
    'Ed}~Z@=YphV9{KvK+{_P3$1;@A31G{=OT0t)cf7ZYh!Ll0ng*fSzvecG%LU5F$FW$1%v|D5Cp^lujznc-{D&SbR?ksP;C9oBjlTvx*2PH-$XkTp8Y>nLt}Me'
    'T^&sd{}aVSe=%F&Ip3T<M6eBh>8c0at*zb0&X&Ck{s83;Nd7M_&M!`WczxPtpXxe67+(+j;<3R7>^@Q|bXCUBejN`O-jo1gT8-#`1Q%#Wp)@2WT$?o?IPvvX'
    'WG#8b9()mHZ&eut1uMdYP+boRlT~>IAiye+p4%~}{+r*_7emb6j;+iw_L=aI2n6CiMLTks9hSC7!y04@PKK0P3O9xUfciHXadfcXfe#hKakAUkHn=ooKF0Hg'
    'amv?OHj?Dt!>D?&cd*&O9J2cdG5cK2qrLimB)Cb~Mr43==x3Abc{71ZX7!&a^Hg<fi>o<kNHr=FOJ?4wNd0bp^R4pYqDy<kgg$vAtXB6D>_-{C3%rFw%@B~x'
    'P7#hwRNY^v-u>cwRmJX9R;yd(^|l&R@m4{__*z9Oy-;Zl;V&;fslVu64`-~{?uQX-`;4~s@T7z>mfNf?Nbt$>0A!m2&RCe)mfX;QWg^>xT5-C0tE3&QazbXR'
    '++<x&qAlZpT;Mr)si0$g8O1c|JN>?}a{S38I`kaBvhui4C0?ioJSvyaRlL+3NH<94)j2^M2&fD5w1~+;PbbP%oq%s}!YO{pY0;0M`o_pU<S}nL<G03Mb#CTR'
    'EWRGAXOgYkyq=pnR2q+;0+z#nUbao%gkng<f48Iji*J<l^F?{K&y_g;IcDIgSUon4d1C5K_dI?Ty5ft+0xMeV5?;gC=&q^QCG`MiXn$+_PhgkMemgz?@%7p7'
    'QFTgWg8>P}^XfO~!Fh8VuA`HiJ9zg4DiWhJ%078A#gvHk)@FlQ26%CU0n@E54h83A0u}TRd_NIv3c>$xHX3yTi$x9Mp_FieaIOWoeh%^y#?wD!2($7I{cvrM'
    'O02*}g&{OT^?_7;KUtEaCTG>;#Ey(7G`X9OvPFg}x<!4^L$5%p>SNYNUpX6b!eAnxk1KnqqVbB-UwnHrQ}^sQ@9Ld=?2;P}UcK<Q7F*!&&@~K?$!%^Pvb5k8'
    'ita)LicTl<^~u|}r{~?b?=CCdK0=PMQnAvZTd+cRZl!ZcKbQtoItY?Rzqy`@B02?n^$JTV6}|*2D5z9?y?TYDmWrp964(&eIj1DwSAi<ELJ-jvKm3*|zwC><'
    '4gYjC>e@@n(pXPfx0^&`3hU*s=nAVc*g7;X6LVRiZ1fe$oP$+b<LKd5TcN7g6<M&#Fx@_eclo#-^FrP&tsrR6*%?H1Y3p@)(O`c#dnwVwNeEa|u~8Mg4xq=J'
    'd?2C!WA9^&%sMr>TN&k<YA=bd)QA;j9*xK#)H72{+5miZWk1si0}wgA7lVX{e_X}hk;!qcdF_K43&nbW2b}6wIgb>|f>>exq2gyjB)uW09%P+%#1J`AcXqJX'
    'y;=^)4GjC2Pf!?Wy6c?sFio(mI|+W!B?B(B#$D{v8?yzG;^MiL_SF!F?}y{w2)ND3e6A`OWTPSC{8XiKy-5)G+GREIvsFOWDpjvG8^8|2v{#t7lZ*%2il`GM'
    '3`btn`c>~eF}}eA6^PlF^9`S=!|ffJv1`Q`$MGSBNr)16oS2To8#9P{O2zWZQaHZ&BA|D~;cUWvLwqi46Q4!ZF-CR52eCd(gaX9m@-Vt$&`1-7W7~kRMrYRf'
    'Q?0604}5iHGjB7JfNeS;vbQ^QHS}?2aTj~F9|uC9%6;Cv<580&W?U<gy~awXIk@R*YFJv)HC<j-P;RIsMA17AZP$|^8=&LG3qR)2s2*4%$u*ywZtl=X<)K3('
    'v!N-YIet`IZXS6LR8{MV_<E?RGe?n1icqkEvS<e7vZ7d%ip@WJ1&Cka0(fAtA-Iank#%7&j0C1MX(@d{!rWIPhUR$er%ECAeendCcXxi6hpRkI0?}2iD}kJi'
    'v$`a&8c)V`NhD9mh3M_29ks?c8D@I}7JK-q&Pl(;{7)?J32@_>q@J*`IiDCKBqHz9LtV*cbVdX3jqCs<NhF2~LT+u#Im1k$iy0{<7sI;@<3<+CsRTJm7v~)P'
    'h0sfNLak!>Fr7Odne+ZEyNB*|-@S%e`QN{uzPljpc57>^JIg*S38)rd{(g4;x6^a|j^{&t=V-k^PJk6a=XYYcX^Q|a%W5zl3%f(Xrx&kYa~`PbPO=jx)m{4U'
    'p8R*0p5T9X;J-HaF&}jYlzS%0F*#TBY7e%4{R;Pgjej=rXS3tgFzqdFFv&~8DJbS%O?V@9XFFTylz+Eeur;Wv$|kqjLpti+T@88>R@AQQPGOb!h&q7h*Xb_v'
    'vB?!u%YO~0h%b4=#hY!65yn5+wMUv_J9*UsGP0J3*b_PaB!(pH?qEiPx|P&g;KDCNpTeFQDZOI;OCD7W?GybE`a#OpWX?-UlE*mziEP7gG3<>h0kCJK_)&6J'
    'S|UIlqQIQ`jOAZddM?V4lU`D~oC^J@NV*)F@lVMExgMxZ*Ks&1VvVi%hs4UC!&AV?{VH*qRwyZY#ePYN?}Tb64Jgwvs6W(|xP0h;0iuThvGXa4)r@!{K59y~'
    'd5$>(<UseL>!lErXgciQqMIyKxv3VsH+V>>s<b=XZFPs^=@Kv5-ptu7N}#|Em+JFC-z9pQG)?b)%too+$Xx2ln_Q_wh3=*JJuZVx=e0@$REhn0ta(L|h!z%>'
    '%S>6*Q#{dCe*-;#-rBA;<7Xgc?KKbLI!&KJIj4cwbXSi<w)x<SzA$9F-@|}gWO=h0#aa&7NJT_Ao6phK1vH;L2RAVY49-2r>~d8wtuW4kn@ZA&d89h;;od^V'
    'x<6Xd86@^5QY_M@?fTfI-9+<lqFG>T|NQFwv=Y=xD?T;3)aysBra+9E2Ouh4aT2-;)hsL0soBldn%XamyJYqgZH;=flW=V}6X4U-vpB9bLn0+ET$;8Hm_9ai'
    'ZoK)B)|$i&a-&T2n$>wZ>v}ossw);-N5eWwtGjhoS^TVkQ@^YjN8(lF4Hh@;Po@u>2&9dFNZw_&OXsL%$5K{9^;R2J1^8`RmrkPo=;$g<VPaie60W`Q(0-dX'
    ')jgNe6(fx2Z+Mj`){2-GS}b+Dz#!|XVp8>8e_63_d06JOSqAZC7zRauCNuxi6?sKH{VokSD;qu}P|uo|h)4*jtBgCuJ(as#^p;AkEQ_Lb>s(UvxIYg;E>6Qj'
    'G8dBN8UwwC19J&C*>e0IwtvF{h@(-M6kN7^4_8;pPY)Mq;C{<F{snF_Y{I?BzEc-jE*bT@b8WQ<`_K^WPMgQ4cST`A#WlcFn~-<fJXIP%j+&KLkv60@nV499'
    '!`$#OtN{;}>{@swhjJKT75BZ-Eir6Zmr}NpyIv(xUn3FWiW5&p^%{vSrh*1wwd&ro*diCPbDb?`2wv<hF%(5@EB)K(xQh+XtS#e5aY}s_FC$O#w`}gEd#?t*'
    'RrgR=6W59_N&8I0SMkMpKTgdx1dfEe%PjtnNMEh=OJ^tMzV-FtPr1pEyaaDAvqeSo#Vm^|Z?h@JWN7V&W=;4NoS&NN+)=9Q3n<E5s!lwMMbHD3;j;4L?Dgx@'
    '7Z+Xo^79k=rLxjFlEtrSOUs|mt`470p#TH}hnMc@%Sxw!q;Q&*%8L`cC}YiEYc7jifQNH!&)QU+8l$!#ucl(GdII%Hb~B~R`HLj!Al|C?a7eHvlHh{GYeKu8'
    '%<j;=X*d{@i_##Y*a2*JzP!F3_J<sp<t{cXY@J=7LwlsPO)rhW)0^Ldz|&dp5_#k@sJSgY?s*Fc9s&2jJG5IC*p%S6_F0kg>zou!$PAU#nl-4?-sChh#xobn'
    'Bz%FZ%3~{cFBG*EP10dHc=R&PCB00GH|MIeQE=E)#p$Z=<#b4S%i1FMo%PjYFFlN^fjiHx0jhO5T-R$unI$bvTk2}kD)g|THEACYo^MCLowjKJD$9;mmSvx&'
    'z44s&T%6pzDL_c~69v1(xcm!*wI|y&VseoZ?V&d#gETPJn-o~dus)oUhYYN`QWl~`L5F7Uflf+~1sFaj(;)xNJ@oj3|J#E9<0Krg8LjLD&3$;$L^~b7+-pZY'
    'tn7Mty|{4{ax7VmGfp{&jlt(6#<QO8YO>@^1TSUuJ+z#2k`)h;hw>0imotn)%c3ed6Er1d7itNI@5eY7+!N6y@Q}6XpYv8PFutDD2o!HisbM4^eN`;?{e=SW'
    '6d);<Iqd8rq~?UK-Ebyr)?=`n468G+BGuh^GkUd<J-`rJ3=EdBTPNpdA=F=;7)A}$ATJY*MxQLCxHAH*;tUa#a0i>CM2k&7Gok>3QNBhX-so?6j|nmOW6E)Y'
    '=v=+Ij2V@qznykZU%&e46+1z)Km(WSdlU}&wW|XKi5IGCHoN3UN@`I3h|Q8+Xa^GlxbG&n5-57weFt|OTBU@$Y?Fn!!r`)&Hf_iXhs#zt+O=ZBWvMhiqHtOG'
    'wcq%{wQ`^w)ho<Dd`lId{SJR`)89XxoxMASUt1Ix>xyw|)NB-WHI1ILqANuyXGOAUqanE23^|IMiFR68JN&XjKQ*N?_FPxq6Hy`)$lpaZ$k_7~u}!>2mKZEL'
    '%)iuOum!#c(iu|K%{i>NFsnQ4LCoSFd-hdwdAPIzxV4K2rJ%B3u!NcfP`Ps{*p;xO@k<<+2u2AH%Zc`gYCMU3LJ+roD_TD8J5Bkq`Y^u(2+l)1V@4TydD4l}'
    'hCN)L)P7{_h15+rKp|&hYdzA-&$sR9BhBh996oZVw7pSoaeK<3zpPqYFXY<U!3qyk+a*&PQ|up{@c0c`xvY2u#j$)jVcP*El^o6~$Lq<~BZZvjB(w;H+<AEP'
    '%`M)Y{`Snl!)twEco*VaO#(YA&r&MHAhlu9W&8EX+m{vOTTG-FJ!kS(N!03f+J#b#HPJ<_APElbdY($z^NgDREK)Svf*vwHJL-QxJ-s%>`F!nWszR((Fe$gR'
    '!xXByx;>ep$Bc?Uaat>Hhjf&oP%sS6<O`srd81FJJ<4%=UIKfK#f&8`2b5UeEo}TQuxG{kKsYey%3eVX@x4Z)0pD%$Khz-y)HQG%z017FBE9NVPi`xLd={MX'
    'z6kks73gc2_r6dm=p2R{vrbWZ1z@z1=OrHWE#`t_sKo0D=5->D3V2^abQDWAAzCVn_SN!%><*c5)Ks4HDx%oExB<~~-WF~T*<uB8^?rsdEdr-vDNL7!4uZr5'
    '1FOxnN~L2$Hj#MRiHrhqROeJ5Go*&4Lrz;b?>aSl!wf6-jCCV(#nDoC43jJJy?DS!Cv2=238J+h^#+(^Vj>W&<K<kqT&ayFQ(!nzo>B7%EQ=m90<<jAO?b$u'
    'KapF7nuUSB9Zn-uVG#FuQDT~hmqn&|`tIF}Ulq@~jd6VaWu{&^9P6Sxp0MU$8SdfH9435}b!85nH;mcT#d#5)^}?~{M>`lnvn&7Z$-nS?SDx?6bJwsBRpU~0'
    'NlihR5SACNy5qt}*_BN{F>viCw)*PMp|ET;q^?Tj(*vnP;GafEA>Vl+$B3L+{Ee$%w^*n3K6I?e0#4B>v-(?3{KOlD4F5zcE*#T;!Dpqm{jhH;IdmQ<ExzS2'
    'z_Q%}__7t2Z{;tLMy2isVb=mKt=tP%v_vO74ec=HeFSnMx$#l>ieaRX`w1CBIe^~vBfy%SNDv$oQDZeG2S|TS3mp1CvZ<Ch9ku})wu^ecqDG|2a9cfiweH$q'
    'U6_l>r3R}UtxV1%*TCs`cR9vN?Nqp21SXYz3>{PFx0)qP(^Fhy`79M!Rh6>USa*V67y8sSV&bB3tHjz0>&$(C?1uP*ax1HHF8A!Lr9wL1ZmA`w>%EOH#A&tK'
    'LUq?cNV%x*qF@IeN5{)0cQkyZQK3~9S6K^Y<Bx>Hv(h|^%FsyhpPp$Eb;y(kE+q#uw#7j!SPacsuw&Kprhcxwz>zhuDarZQ_9?Db5S9!D7E8?<+bUh<?JJ!m'
    '&LWNWntN(lQX;`5X5&wk&Y(A~ExmT!I;lKyVUJU;q^<|GQcWD?^~78&3>_U#K3=L{YW0{igArFhCDB7HR<!8BwpNy1#bk<8;IsM5lU^6zwjIkpVtKS%^R;gc'
    'nJv2lqVWiGA`gZJ>e|DlLhLmk8P^t#7dz>0OH9dm@9s4gMy%G6uEeri`>kC{Assc88<TB18WQ|aspo-MBpl~?f711oU>)w1at^wWD<;7-qHKWXJ&B-PvCT(y'
    'N~-wz<oq|_iE_2L9afzUSis6EFSp~AOp9xNCOw=~n|C!2-5nNVUI`=$lgfNky<;(RNZh9!aeF|{oz8Wlsw=gq$%#*_`3YIq3bwdqUGvReM0NfE>J_wasY_N#'
    'Q2|!EEdGi4Wg^zALU;6K%F<h?p<=bb#Us@M-#AM4#i+L&WD(mbS{%3AR#`7Bn;AoK=rku%fU=!TQ2`O1p+W#H^mou*^1UXd#1G3Mh$fiB8`!7$^FB4#rA!Q6'
    't^|XFtAmW_-H@|$%(6cK+qC=Qr2FIf*&EE5+~A)VXAvG~{-H5M>#fG76nJ@lhWV8B?;n2s@kf%}<r^ew-IphSM<Ke&k6xU-`xy%~<P$B?vv!DDI{S^p?#~-<'
    'Vc~zqgu5W5*D+i7#=Em$^%Ht<dh(7^@-`X$d*k<0{#|cMs3kSZ{WMsu)om8o4PGmPV{EJP?=DU*bh2LRr05ntZ}fZJ`F)RaEFthJ{N&?fJrF)O8<<A~?r(k('
    'TaG5a1wHf?fmnt%6qh6iPV+Tyi{LBf_c6NDJd^15qIMAHoZ5mC2L}iLAA9fKoyL{zi~fJdINzZ{MlMuTD4>U9BbCQhY$f)HZTUz}yVG0-K~S==5g<U4)gJ!t'
    'XTH|6Ruv%2>GVG7y_1NlRqMUxn$O>~4P@{ZHQ=>5yv0<Bt(DV%&KdV6nD7&m2K?9z5DlfeFSCkmF<=God=GXWGLsm_DU~`!gU??rOAru94`9y)8G&mWGc$qH'
    'jTq1}kn`T?40=t^h&Zaqqkcv)k?k6lsG|)+{e|}q{+)kf%DH6}do$_xaX0o_0{7Wt?`CYvGJsIbtM0HHF3hsVG^V({e&5e_+wZqkiGZX=vM#~YQIknz1&=_V'
    'YWR5%b5GLi&Ea^EeXRB3*intalwQLUEavWoz?WoKFc?AFbRxMbl?wc<Q=V#r<~g5Vkw+7=c7OZ<b^P%MV;OK(cN7$Am<}0UazlUo5sM?jAAeA5e^?2RasS#d'
    'H5zhb1r!@gAk=6zSf8vMZ;+I>B5|M<;z0H11^Y;^qDEWcj|KdzLq=16an9n&IRO|_Aw~nUysV3}IkU}{*cn~|bk6hPDbayK1vEPdG6LJ{6AtqwJ76$0Krvb+'
    'j)jJzOSyQJUZk$+J%!6_P}>~4eSs5CT|ii7<Z6T_&@(0q`ZfFANssbY=Zk^B(drv3WFZ2sa=<VlQmD-zb^=)zq3jsT>H$D6u#F9>#(CPLr?<iM<_*Mg8GnS4'
    '@gBlK@v~d?tRU;T-2|=?_ox#vjR|S6%9Ff`S`2Ki#=&_Oz6_CUdK!Z0v~p|LV8bAGG0jr!t#sGgry$%mjWW#a6fcW+AioJJ(ki*lp$DUSQbO`w`FNr8zHe<8'
    'Rf^Nu&R+oDZRIM!p#4GC2j;PMF+%!i0U!XOdWx^mn`pcs?0!aNBlqbx#)?33_$<bcC=Wa=3bcri=p#exdJ@AfADC!h+%vuWHLZL-$Z;*jo97IsU)2p$!P$Q3'
    '`1Fj~QhklZ`CHf#rxFWzijx8V&<mC=_)B{-SPUkGWPdi9G9oJFJK}2u1h@vOFHyAZ5@}D73A{lEFkp*7{-odI$qfOUrVS@4JN2%nRFp&o5{ifx{!TrTUxb$>'
    'S1<NPOp2(_|Kktt4_qi*{~v$cHsCrMvMVhOL$CumncW|Ms6Iid8m+l8-O18wGaH9PWrNtP;Kl6#CBUiB8Dw_b*e9i8LseZ33K1E%?i5%s3Jm9I#I!=H%=cPX'
    'iUjFamfV^RJrB4A8i|K6z-M?u><7<<wT)OOo3opP7>Bkycv)8qYkiX;yW^h-HEZq_15dHfgp=F%9Dr{){SRl{evA_kR!cRK@L=7XPg5o*taYh`Yf|XK&^FN`'
    '942gh@gqWsWu=A)_MDJh5Z&zQ^IsVL{P~Ng-6uy!ugx#Gt`IQ35`V$KbRSufa|1JFeWYhkO@9DyAhb)MI4o3X2H%3Pbu1aDCPa0h1MnZ*j`$Ea#W$&aki90Y'
    'H@t`3*D7Na91+wAZbUT_BMhCu(c-u4+vUL#6i=B=oLF32OcuS7ZRJHZrD6s}Wm$1)zH-(BF7g~v0r?iw_;s$Qo@f-E*Te#iua!rafhrsdS7~>X1Vjwf5#EfC'
    '4;o~&beCm=B_4e^m%tWkh;+F8zUMl^jN+fj4^r<1Wuj^P47r({vtR}F6BT#4u?9gg23qQa7Z0-07vUHiAPQai`boyauz-#bk{4nE_<=cuKT&-6BD|l{o&f__'
    'h7Zg)!19m_BM20X1)&xQ-tYrhuUV!w6Ak@@wI52o0jGXQKR)L;blu%hjF8spXyd1-bqLf!>vZIoR_MrYmCnmm<)n?I3>RKYA$i@7)Rj~0$aACBS-lB`3P%-a'
    '9Z&k`(WBVKNDW{%h9fVPe6Hg!+4_d2yYO9OD}jrRv98E$c4<I#)~E=|c%wvT8{|jPTWi0&bk}z=ElcihebMa$!`Zzt?$yd;QK=A#8Yj887OA#sv*iNI>g$Q~'
    '{AQUv@6b_2CQI|#SjvKaY^db&95+iqUu(svuXYUzR5A6PRuR=mX`%P|O5SI(@#YA6ypw~~JuonywkES97k+VpBy?%3onWujw^4JG)c6Q8gWUawFaW6ZM~X3J'
    'q)9lqb5~d;J(l9FhoUpX6DONid1&XNOxZd~rHX@PtuyKXeGD;Uga!5izj--OAgGX(t~RU~DHk<UNV-djUX!T)i1GB~X-IOn$Ai`w8novSRPG8*S*X#KK&363'
    'x>$%tokIb_wwl4!-h?Lyt6$wM8~twKgLb1+raAJs%PXM?W*RMnZ6)C8%jzTML|BbfB1c%(RV^49?i?C_9K7Mw;>Zn2I^5f<a5?Xo81qHxS6{yLD#XB8fiN7_'
    'n;KigMzqA8iG7#|cnI^bAHM3tO|w)gys6Pb=i!8DRF;Um%fhiYMwzmNqs;`*%~e^LYa*n!xV>8GVt4*$={el(r)~QKeyxskvk;fQ<bSsM1gBoS61XMxlC1j`'
    'v6}!dw{|O9DP!S~Tib-TIZD#*M29Gn*56{b9d)KUVam1aaIAkYyf2h#FqCp-?K7lrO}3Pp8)|ElZlbvj&Tu>LvLXcITWY|)z?o4NTXY)SYQT)5+=e_&9ic`y'
    'B4g!U@k%DQA8E>G_%SlE+n0-&7)_gf@04y4OD4u@lu&FlS_1tUl<}-YRZ3$bpXPBFhy$2>$octb;{xfT-7AUjn=qY5s)fye<1{Y`1IY219M&8=1u@eyUj<aG'
    'n35UqL0cUk>|2nfKrs%faKIC1dBejqGlOAop1?$xab7q%#d-?Ir63M=hn$wBt=3A{on<pGI;I6_#O`pB;Q85z9`Gfi?3*e$Eij^+D+4g<-6u-0fGX8h5~Lci'
    'ftTG#ORBgM3jx=qNP=A1qQ?v$hN}|db8}TheG1miq3pSnUBINsv8orYYo0VMDJ=9F&rc_$ZOm7!gp%UT<!woJFe&?>_%hhu<U!jyv74?D+B$(aM}C_RYRu=c'
    '6JAwC6ISGLQxbEkJ*ieDL?l0Cs0MJRh9ea@I9KZ6edVr9Xltr`c{<1s4^<o5=oD?qMLEZepW+VaUoBQztDK)s@nC|!JG9D$jTNo4H!2h2Sf>$|+#=-!ovg9A'
    'P1u=`<0HM=y`yHfm$IBr;()fm6kCzGs7utg=4Dhww@C<-gM2>kkz>+V<R3g+2L}kIT0_s%RFca!kP=cKrs8%kMSCj#b#)$SUE0r`+e=CVti*fN0EtS5vK;aF'
    'AB(XN-SIY%B7YxU2DXf!U?<SoB)SY8wg6$pw1G=`X4^Tg=#ygdw}a$wG>VwD59wwkQIqEV)l}g%rRC}+`wUaycC{|wO2Nl>RKrfe$B&vVCleq4@!40BbB<-+'
    'zD}NHtHH!cF>Q2K`91D)<fGA-Z&sCHsbr%nhF{HaA_J?dF2vytTfF-uV^br^cc5hR=@qW8wC&JCbKU)h)Pi4mo!5IKpH9jxVpP6b!Q?BSR6)`D>T=CiLBT+x'
    's-~*6G%J!bA%Uz&D`rGG_)EBKQ(msu$IrFXHbN)OIdcUp<te8SqWo{wc?5F(@S;ax=dejBr!8kFxQpX9wE-8<)}Q9PeRRA9^Nv2wXjh@1C$GA{vLRRfeCE7<'
    'arB0sJg^^VC-3IgruF6XH-|4N5W4d6`HNri_!)2>l5dZW=ui?q5B_oZ%P(kGrSHwhK6?m%G2~CaMyDqHE$vcEs^+6tzZ^Y(^$XP<tVk6!FhLap0|E-HDt>bG'
    '7Jun+VZ;?apoTuHDR_4Dnmy8gI{5VvDsDlGQUMPNeaT-x|JT0`s4Tr#RhpiuqB%e8pN@Zf_2gOi<TbmZyH$Hbf}g)19KY(Gyg52Pq|!Y5foh*WIqW_;K0J77'
    'I_1r>npHD~!#A*ze&&kRG6kwWd3kj7=GpVZ(wYO`{d{oz^6>ZsH`=d<JlIutMXXoD_Rhx#mV5qWw$+_wa>&I>jL(EjcdzH&>+MI@3nBnYwU>LY{q}Qr0u?g8'
    '^|r4#z8TDVH#I_YW95aCgz&iqQ={zE-$gsVts3v;F=le52)4=8cU2NN2GTv~JxWXfew9SEIFROA#c8UKLq4m}LzAu=e)#!c*n5UEQ*kY1C2A`78GmG3!J(<1'
    '7!u*9=33Sd_fo<V-WqU3Jl?Nr_SyB>#t6Diq8Z2*j(*Q|%l7*HF=2-oQyji800eSyi`go-4n&anx_lUp2V%KndBj5M7qed2r&fYhJ47GRM~s*vC@(VIB53q$'
    'Dl7J)z?c=n%8{}hyjqF%!ZP7qp?e2VxAjFEx+;}*a=q=Z-`SvpEuG+x)5-j5mbpqhohm+wPJ4^~xfKY93F`O735MS3Uv?&>?(z1ILgUcQ=fK(B%CT%yVZ8Td'
    'Jxbk*I9`li5<6&K`P!86*xJdMVvG8NnwX$pgG?Z`#&-EnpW{GgD}oFod|)i;lO1~4{?JjLGt{UPo1XJH3a8Pfv+X5;qnx}1r99i#>6FNwLQX!muo1maq#r29'
    'mlx$VvOg)%i{Ko-H?D55&N^I$Hs;rJ1v9n(b$r3}J^LljV7%d|GjvviPGP#G0<SP)!_g~jsDhn_?!AHDV$)f64P~$k>v@9F$<g&OBT-~GFePC78y`t8M|IwX'
    'sY#-5(2dEur>F{hlE>F#!o!iTcBc4>^e`N)nX)~gvg?Q)_Gs=r9Cm!mLH*ga@evd6t$NgKg*6xKP)4SdJnumk5KPfT{0G+SdBTL0#Y2oi;`4kunT->2=7mav'
    '%H7+$na{@AjdHl*tdWxtk$5**xNB~c%OOUA;{`2VHTG3tNh+;E4Q>rPp$?G>pr=pY9v(jB%|S+_m_fs(xU$^wC)rJ#O^-NLaft$$#}Y7H&}Cj!H!J^Xtm+Y~'
    'xoNmo4^r-dezc8fbhpKWH;m#p<%(<RH|#*JHe6B-0^3bjsxY{y_^!-U0NY&ir}=D#aOFS+%PC1f2qBeA?qiW0jC3Jq6GejxWfwF@wS@C8<hQM(ZyX@qA;IZt'
    'u6?>NRFhF@iJr-n)ukbLs#pOGY0I(ss@&ve?DZztdv0viRg>6^z~a@prg*LOGb%*-*nEp%fJW?4Hk$(1T0at3<&V9yyQK(=?+x^<qgpQ4D(7{zM!BRk=WuTK'
    '<!acE9z5C!%>8;X<8DTZQ<8C2m^Z5DI6XD&hk3RDzN>dNf(e*yKj>0n;5C4+B^iucCAl>3-Vr<*O4(IRthhrKzk^q^b@4eH39Scu!tQL5Gx!^2&dRxl$ulmO'
    'Q}|1I(Hq~^jB#Mg7=_9DYvI3gK$3!It;EJotgZ{ai}R_B*Xx#R*RZnjl6fQc8!EMHlW`%}*8(a)xH*=&#+!d_?g)P^X@VQ!x25pKaKv=%jn?hvVsAnYK-eaX'
    'ntI+UchW2HcQM_+2atx~tWwC(m*O@Q)sDK3F<nPXHcMeZ@v5$k_qNUKZr4*LKh(1Y(YYmeqHma!niAQ)l0CX~*Ibs|rw*02$uW1%=<mvU4LkR;yn5QWVbh$m'
    'wM+Zy5rQQnT7Ugo%eTgaxMRzqVk3|T{0^rP_x+OQdC<m?FLqR31MEcE*3L0JNZNpzBO9ajl243XK-RZ>lq*<Em)JRZbOpQ$Te>v2^6;U{u4se*vTO3M%EVx8'
    '#34@BzwA2U>fqYyl2nd-D{XRJGqn~VvFx%@^i`-oYw!=D_Wa!T_s-YJ_wIaHFYFQDnSCkeB8oXN`b?{y@4_A4xyyKmB#MD)!{vKFObi{<zuB1o!EB7jgb+kS'
    '314vEObRw@<IG&f@x8DeU*v6hs$vzzg(E4KCkuLf-5XtHN;_0$)4~oXr1)qeG)yspA@XWbLvDeQAYcQOj8_PAjlOW(#T5uEZd7xQ(vhy3f|k(UGQY;~fih~L'
    'c3kd=B$4$<(_Qv=ZNzce&QO4s#Z%4IT<UpVzP?t&1ufqI9pi~5|2mu*hFzPxW`n@I;(2|{lO?sp4$&2-ADnS{kH=ZTV;lbr1N{nQq@34Ww_ThQ)i(0QaHPua'
    'r*ESHV(y>=mzo#!?%IpqA*+Obycn_z6oxPL(_a4rs?2*cEIGK6w0os%e0Igau4b25{fo<`jNqjwf9*VqmrEYf{1U>l;vL5tNV+Y8<kqZtxd=&3^~lbHTM(;E'
    'q^I%H5z&W_R~im=5^lq`=@_y2H*{lQMa%1u2?Tk$yu3(7vkW!1dY3LO?@LjqYW_}ngLIZ{5TFjkL1OXk&K-s8Q!_cig*`Q^S}tPe#k&y(DM%Dbk%VW;xDGjg'
    'o`g5b&K9;-+p7`Q6dgGeIPD*CuQI<bJS+YKQ(6m|N)T^v;yU>hYboz4(iAK@cXG2g7|^8<FKMulB{Mn(CHPJ(s?MzxbV24#vr0T4A);5Jcc3|6QUx1q$l2D0'
    '^AFjW=(_Ju;HDiGUijK;2gNBIEp2`k9mG#4LMU|gn-5B^|NCLq6f{_UMGvH9QQLL$fVsSyEHZR}naqZZTdy|eFX)WWuSU>m9_N>Yipgw|4Ql%Q5SxK7<09j^'
    's2;j<Zn!2w8F63Gt_Vk`VnyGi<;uD1?MDUO6Y$yL1fierG#|x0ls5+G1jqLV$J|<j%z93#r4fQTlcRQWE&FT@x*MRmup|W`V#+9)E8!`8DDt3nR~n`Q3rlU*'
    '#*Dw5(Z>s8HAWvxwkLAC<~{>Hq|mrOxf$yZ;cxdl&ndvT-`H+X9PF&&u;{<=8%^acWkyFY<(o15hJP252c`TGufio7qGB>5P6jQ;u(9i5c3^>B(GG?5=xU4+'
    ')nsGFPnFu?^HT7svH%tT46GKSLcX5blLno#*pWtRUifHIVbC1~*OzzcwcT+oUtMgiQWzv-hVq|IZ15UEGE|I=%InR(w{ylHy_sAgV(E1@I~z@IqQzu9L>A?4'
    'DGjFB#GjYb;92+N86}=>a>4=l4dlg2H}FgtvJ)pdM1^4N(En4S0S*+=VI2>W2=hk8R?LWs#K3p(|J$5R;Mu+BGkE6ZCwS)MCpho+C!<l;U$}V+&MAY6|IEoB'
    'aPFijI4AcIE1N(*d%$@?00g}FJ8^)S3r1F8kQ^K9-ohXL1hl3VwUMSwrg4X}G>>yY_kw5-ea}7$F0dr+#ALIRGtP7WSH`jbO8F4(9Ui|Vk8~2%tjzBkFL^D1'
    '{PX{-0P>%$0+9dge-uDIDn9er$g;m2T}~cKpOQw}hKfHQ4S#ul5y!K;D9?y(DJji2VznF0JCa)gH9dFFL{bnLgd6cIqW(Vn>!JQW``W0#&r0JvG=}e|&vy;o'
    '&>T=9;?uLDz>WVx2;8rSar-waZ3vZCLwvceCJL@}GA{ruZMQ6N((<b|7(I$ba1!_;)#f<NqRxTqenQ5|>d~ck3e0l3*Xz`3V6#pfs1dPN@1H~#Q(B9Jt#zcq'
    '!Hql;q9T>HDb1vb7WGKbkh9z}@ES&9<q&U8IO(HD<hM)B<w+6Mv@e8^etc)T^vycxqqlcJjFnwjjIw7T(d9)BACJzfpU^bnQ~pc^K_z)d5%B@{QeP;W7ALAG'
    'gysxS#u=Tt)5&DyK$vP!Q97ztqlDQXYB9fqQ0&Kmb#KWz?KR88r<3uOOgZO-7=#h+wDu#V3=&j(9d~DLesoFYoOQb%G%e|^^DyK3L=?aYD}F9O7Qzgf?&tT?'
    '<bEF7+^U2cUMu*gz&PY?p+I*-Ym4(}PwaYONQeP7)b3I^$m?Z!Gw3zF#H1VK$}+D7X5OpNs!q~*=uctSsD5m~o_H*r(X+#+!2|`*3>J^0i7C?dhey5&8m`xt'
    't36u2yA-&cqhJd4l5|bTkEnHAv1(nu?$_wgk^$7CKYeD@Kti?UG<76qRXz7l8s=Wf*HnTAr4@`l3X;67U6c7$Zw;q0y*2(+bg@tj*b4As0Xw<5q-jJB$h{t9'
    '0m{81T>PaXl{V}ed0{K()&fFU;>KF+b$72oXlf$`%t*@jjK`=<#VXX$8AcH_+6vB%<shC*ZEi*5Sr$!@4`jH!vm@@3=!IesI6a4#MGiMbhhFwwy{OkdWhn!P'
    'TS5~4CjrDclX7=}xMzO}(-&U7$45smH9j2TMj|<k-c2Thxk<s7MP%?|pF?#U-7TdzRzI6eF8(wF*vYZMbbH9ZpB?>nOn7Wt%_Q2|f`7JSej}br_Y2nMIgWBm'
    'mceR1>*A(SMk)BoVvznBwlU#nf7_UN*}j^(Qdj=f)RiSVKBM2$8z#gl>z6s*o`Wo*&^Yt~(CWJs^>-23+ZL-v<rnDp)=<9QzrqihIMQAP*f+bfrAPo+Q5@f='
    'Zmq;olSnJIpO0p_jvc9L@;)Sp-5tf8xQJE}(#w5$6Wz^|$eNaV01SkTOu>QO!R^#)Ys2w)pLo9RwsEplm22B43v{=Z;#EuMjpf=^+?$)mg6Xd|;g1ExdC!~~'
    'N|YInx;n>Xz2zITL_u(G2Gv#cwH~MlC!D}lNZ9xm$3;P;sEZL%Jg?4TJq@OAV5dA*M)U^ndwsl9s2N%n&W#<|UowY{z!vruiT=%JG|WZyx;wT+qZ$`CA5uLO'
    '_r%k6>ugK2E`_V1Pim#CyUlP%=-~b=(CWG;0-ZtMhJ`?SRWGcTP^q3j`SmwhKHPk;)RwpU9T!w4zR44hyJw3H%ytXgE-0vf<Tp~P%ccd2ZKyd+hT~g^{e9A#'
    '_WHvGYVDg1QQlh1<$UZgPUHs`(CXSmQ1_2Cycn~j*=RR^v90P|jYE+1x}Su-W+vCx)jFw6OCxBV6ui4R4U6R7_4(vHk409tFY`BP73SjU-zBGzo1eF!2As*Z'
    '&a4zxiqavlYEy@*v`T9={Cd~7srJclE1!2o2d7(Nmv24C<Oy;bG~Zz3%V2j);6IT4r7G-X5SAj%RP{I<ZAX1KAshu?t5^kUD~`RPZ=$ol9b|*56u~w0u6wH7'
    'sSPKHYH5{QSpt0zsGD?d0<1dGHN*uD?1lQYmGo!?d{X4(va<3lFp6TUN=|vYK2)2R?8Ctb$?4dPUOuN5(~InC%y37_8$Xq+k>ZR(Aats|f_%TT%3o@}vz{%d'
    '6<e+lb31cqg_y49KdTUXc6j_$XG?fDnZRxN1MHR?_&3~(aL@G5CvZd~ka1BdhSy4UE(NDoGt`D;q{0d)#!9tf=h<xV=jBRx_H>I=4#6rt+L8xvjxbl^gNFP('
    'K6vvSpENhO<;lzEue!e+kRI(pgP@z~@r$FQUw=Ayf|(Xn$)nfs?JH8ERi7NattL^GJj8MNr~rC!Ao<&TsCx6;o8RP7gOob>@Z|O36XX=cM_75Lf2#B+1XRD>'
    'K-PhL72wwn1&FXS0{leBswvrwwg?@U6yH|XgZW|x53XhzK6`Qmy!~hK?-oCI-OP^D%tN=CE#1tv+l<lxI_&^2f#WnyDaU!;*sjyq1Glkl-Pn%Xm{KzqHuhOf'
    '>9eEP-8a9#W^a7y#64zoxYs-m_ny6B)tn7qmZZU+ZaYeWPL<L6o)5OVgRBoM`vjwyDp(CZBN%7>YnI*2;Pz3<V0^@u8%sx=&&+_u=r*tw$y9kzlT2L!!R?k}'
    'm7rJXYcKo_MK9?{Axu}PPO0J*ic&P#=^5O;SCpdxC7AN`4BP>@T^?*=zOL00F(_p-e(R0;><UkdjJOMD3;m#I<W^|H;m0ZI2;m}J%z6>cRK%ZP!~yz(UZ9->'
    'CL8AC0$<L0H#{Mc639$Qf^-KJD!Ea(-8Zhq{sby*i!)_0TvJ$!S2*^@Jnw^ucQwjt>@Y@{B;o-^i7>kuV_^;dH`00a#u5@mK^Eu3d9=8lX0lG0RcIV#z5Y45'
    'nLSQ*J(%zlrwctJqTU<^oegBe&ilO)ry<gJLTm+Yz?|!y0~bM?TQ3Yz7#JZDg>u!tJv#JdfLhx^UeV2byWzq9*9M$gTYXaZK8e1Q2bwGg5tcEz!+_!+uUKjs'
    'BzR~DBVZGAeb%^^DVa6v96_O{p(JAiQ;6DR%3}S8B%*Md`NCSTm%Z6LjM62%nhB;dz{p}1&;}3w;LrbPA&W7b5jyWIyUxZ}giv!eC+>!%5i#D%@u$-BtLc<h'
    '^lHxQUYlIa;B0_&j7|l7q(oC%7hL$@+p^W>9?ELd4o_v`)wL(@cv#)Z84*>yZd!^}Pz1fjSGqFCwbZrynZX$)Eluw>5C~*DDK7~n(l!EmsaWY;ev9nZ%W#q1'
    'u9f2gi<>MLBCo8G)*`z#i7k8;AJrSyHmal-*=;cG#kXdKd3!)7vsomerrFFSiPhymRHS)`xxt#Umf$GyyDmj4By1*fktnQyEI&Doq_T0;!~v@sX_Jv)<m51Q'
    '53S|o3lu=_!xAqQAOcsk(g89IUnXUqx$tk)G>8{(T#_+B%gHj+Z8Mu4CQ6|<9+i^J?qZd~DVIKp)h*8HBh@4RFz;}PMglBs4Ob^=U?;?7t=QHI*NEZ;1CgK6'
    'xu}M`_Oxo#-#JScN2Y%18tB<2Bc?aw^ejBr-$t)Rgq&;XGU|<HS#NMlxM6T!&(KSmZ(q0@_M#r_^b5FO>+>P}r#BOFJG&Zl9dqQ(u%gYoItS1Pwq08qN;&I{'
    '{1ki%QoA%Z9~J6vbM%!a^uePC{v_TjETJlH{0s87Zr8<Nb>D4NmLbpsj#27xY{BG0&YQJFlZG|e+BE!ar<xYqrS+2G23MgvU6(UbmQAV!t()-@#Ned|V_^b8'
    '*CJ3~a#%`S{A5e6fU~6=()nq;4(R9MP5|FC@2bKHpS`Yi!MOuT0`<zN%x-*cHaO>s>sy5qVfGIi3?`ZXpr|=WXlR31AQtO_S8z4_a^4l62H8{(VNAG}Szwf+'
    'r$Eg_y28`ET+n0&S+NQrZh2pq2yBXjW?d3;%nCLMIF<9-&2Vwvg;{YJBC?iq&Mol+EKJa4tRIPDmTA!vBMk>+5xrEdq`@}lj1f#xC2!BEcCn~Y-1s(HI;bN0'
    'k#oU^F%Zg|nduF8>b{qz^51Qw?jH8Gxx1n5mwu!PP780h;#_2l8c=6k?(sEpGQnJAaD3G|1<tSXzA$w`IlEgS?-P#%vgA<|-b^CTmkz=hKzWyJq+D?!yb?G2'
    'xG<)}TCQf!FVEYPYTwg-Q180v6M~0;0{dc3b-MWtO~ufKS0N<a7*Fw<`2-icZZ`rC@C4S1_fx%OKNYMS9VDv}SD~ZlS30R=byB5vknB0LVk^6{{&0}lNEEgR'
    'ttGi)*Djgkt6Lv+yv%dH=suUbT%^{H<Cuv}<a{v|c163w0~wIX#`s;AqFSghMq>pqSny&9hznW_0b=CEVKV>>|5zO^h?MY!LY&1(y4gl8y=vQ4s^X+n<{yUB'
    'R(}Gw4eh&mB|Nkb%aNpUDP#^mbdevIyYB-6-N=n~&A{)|Max#zB=Uh#*5F>Cil-9ODjEyQ6hP6%wjo6+0CGbW+^kAc*?d2NTcq;cy!G9n5`72fFo{INFcJNN'
    'fW|=|bx4Z3r3F?O24gqtKnYA*IJ)+PJzN|!kLOdx=CG8C=k~M>s$8(k-t~rK`5a4k$U$(T;*lpGy5!U1lz1$vBQ{!nPa~mk667Xgo1H-7fD)}yHBl9sYShuJ'
    '6dRtY-<zLn9szfxkOS!dtsSU}>C&*{sw>)BMn_zA8h=oYNERBX{QaPBYwFoXwA*O8!TA@HK}O4r9bI|fe>eaCWGCQfl7d+#!Zn~TspvzNO{FSE2XH8<*e41}'
    'DfC?;%y<|D>OOqAg0gRk3T_Etk7yNC3D1GpiT!t@{<ZUu6XqYUd0VWylja%l-Lg%MmsGQ1Oi!(7t6|JfXf$+9P*}R5qY_%t!-geVXlXU)-tncvsIt(yclp@G'
    'kT!Cs=Ywztof{AmDlag7v)M>!-bfK^-|lfBM;vv7wp{2Xd7L1tjUnK=v7B2TtWiBRpM3AM>Um=L2S*$0e7_CjtXwp=+G$xPSA3RF#2eCfXZD%bZzI}5*wHch'
    '7i7KJXqe3uMkU#6L=}X)Sb@xIUrmLeg@LP4?deH<H~RKL9B>_4zKZCVRIpuw?o~Y7moUu+d5+EcY=mdqyRwq+HX5JVcU+b`@AAb?pMDok3cTp-4(MaIw1uGi'
    'kzEyeZ#rfG;}~a)*>)qbw_Es_2G8G%gIBrHsODk9L>Rr9K-07Pbyg=Jq&^78303c^<)uLe{V)#d9nS)RTMvu+1IVe@K60vCgC;^Pdntr-F5$PG_D46BFE(bT'
    '@A-?TUE(yo_Eqn>5sDV)!pe=}%MU*`VR;>^e$mkv2jzq^+&@uH&s3z0xaNB;wI)Od^}^EAt(H$VS06-RF1e$Dqd=Ih3^7sZXzxi}&ZNM=mfQU$(`A~@O%YlD'
    'mM$xQEDnnIHbK;FIuxmcG(erC!N)56eJ&N0IN1OH`B^PCJ>g2X0;mVk9RmaGkYOApm0U6}j#G;NRUnR6t&57c$Vc$15;}&Lg4wK|xxoN#^qn2<ze2WGXa5y@'
    'I|e`mh=t4>!EBx3s+o$`3A*<clkAxy-o4f&Ini4AEWa^3J7E7jKOC;`aWEvYn1fu2lU&PD*syL6+o6P}dv+S$FZLNOj=|^2r0#Uq%MhSetx<CR>S<`Cx$|dv'
    'd(r8$zA5qUbwoLe7@1wvJcp9Cls+gdTE70cTbS;n`dY}Jz8YF<U*&6C<t_QyEo9l&sUZB(%CCY@>NeBw4x?y!G(UW!p;AqB|6aW~Mc$=Iwtb`2(-Q>kVQGnT'
    '#wGuHfzGD(wIiL^!CPDv!*QY21Et7}cK~D5l@_2eGRQpIb+mT1#ejGSFoS!kMNK9vCXmz1*`kaqvZtg44gJ_y5BbqL|H>W5*4(7%KgtS1{iotw(gy#wZ|t<O'
    '+Gt!#qiSNO(zFq;1S(mK0EsCm;ibf>&)F6iSVei>hQb|n6BmRdS;oA0Wn9bE;@E^8Vd~-sb9nUB949BY644LriKEI7)nyD8K8~GNWm&KEVee0-x0?f?Eciz_'
    'B*a(ll{8xx9+Fd7-!(wQRP-Ot7I5_T<n6(06(hp2Au3XYV?^BG5ON%)aymfdPH6)sH>jQ|2oZ^nv&*aDESpONOYd}YoqdgD0w+3dWM_weQ`iVck-#rEY6Knx'
    'f=1w}9Uww-Z8eGc4Y@5J|MmjC=Bwk$#c=eYDmC464uKOdhro%GLtvis&4)+EH6MO>p84?PbT;{rjm>XE+yj{d=1!`Cc~KsL`QI2X)?Cb|y&FrnltfN|_MZ#5'
    'zZ@XE6c~IdAb1fFxJ>KaVZYreMe)zI-h5!)k($;2U<QSI%xRF33sEp_fk9OyQVTON9riz5P3ICjFt_sM*@8_jDMCiBH_f%uAk6<~r$IpUk~9h+{Fi1+I9VlI'
    '!pS<>5}YIn|MA=i7Urj`V-AIJ)1I_*AuuRR5X~bGZDBQKV_@Lpra~Qk8){e1fY<OcybEYmVwdjFKcm!Lp?h>P%ctd>I3m`&eNk?R!mJb2LM~Lo&(KhEb4k_x'
    'b6_Abqdby7AvacPPJsh9Xh1xA_cp;-B05nu{*k68mhU6_mXdGc%banTt09$%Z^5y&ZeHPir>tCH#$iN!X+BkWuPfPDcA)-AW45y-oL=1`iuH)yLkUtj?`cKG'
    'ven?a9QRhz*y=mS^NPK^>J4BAEEJ)wyn3rIElf<L3*cH_QtOv&=Xph8NhcJIbb@9c0ymX)Q}uV+t!Af`r^)RIp6XV}dbYNfjh!}%OitF&U^oPijFgc&%0S2`'
    '71YnxDsSoKNB5<3oCqC^r}Xq{(bef`xuej77e`NiMX+;RR(rYeAKeiczBB20=YNX!@lvbfk6haUN@HzTw6&{%j8hWUYPhfZ{i`Vjlps_GIqhZr$py3$q2C!f'
    'v|_v>YkLXUA?H3jnGt`wIE6JmWmbm&h6O%l=QBJSbk0w4W^ma_qj?I`y9j40pnA(k<ehzLlJUbPvv$4d-{vs)ZFNdJy1N~JpK*kZ3<(&cA^dYGqf$SKjPVI4'
    '{(@9pLmt!A8<RrP;cCO`8Fw_MnN)q|4u^-LNK8ldlgHw|qqDEx=Mz0kX{JscN?<m0r$oo?jfHkQwdY;;FDb3)$3^Y3bjnnhh!$tJF0H=Ad<^5_siLhcwQ-Ka'
    '-e^9NxtaqdLT$qoh#)E+%)XB1)6sC@2qHKhl{o0+YbFjl`OE32l@8%P)zhlZ0_}9UN}6uT@p=mCidI{w8XXO_r@g+j!dmNBl)l<hv5=0M^egHwTUo6&EAoT8'
    'u%gOZ^epn}dYbBcQ4_C&a(YJ(#QQ-g{WcPXHFKA!nw;nK$|2ib!0u<W%PZOc*5Oe8L-xQm?1GNWW2qeW%jzw+3kH2_w0+Rqv2J7lAsi~rt>x=a%3Gg@zu$-k'
    '6y7xO8Y6u@j(mts3j7j4v@cGtoUgh&`H%yp*SRVzg>zt8zJ)^#XLQy-SIYRU#@2(zqvrMx$A>4sy?Ar7c`;}a3|O@DkUR+I#*=a~9^FRM-f%!1AOdJ)@7__D'
    'LM>s4mhhz!YP}gfgr3$mn#tDgPIQq$9n{z(ZY$oCs;w`E$komln*n{uq)Ww8_WlHMX|8<FG{#So1Kmk{)EuTPbB*|dD;G}M;OX;WKd?f-2z>C{sJSDPsCZ_3'
    'WaRCopWpTnLuE0UWvvM3r?E}*Q*dVWK2Vc@mD%V++Ulr=w3Z`BxPEJj1!5_20g_gjN(`C6GpQsNX{o^LE*uUNzK7e6k%MDppz_((D0AHXa|F!`Nm{S{55-AG'
    'toRzI&BB<PB=SwGxv(0-{jh>+jO{7@ymWHzDZ0j?uU4du=}SSNO(+KaMg`X3$ikPR9XNv@JQi)K9gyON&S=9ON6x@U95+*>=wyA3Z9T}FhhcTFfw(y65o@u8'
    '@{-s`b89Dj0V0#DB4QGeK#D#t-SH(+GGCTzW*PE&>6N)c=sK78LV{MDf>I~n6;slb&gyuAOHxQhmQ-I_buJny==eZWYV8zFJ>ijvJ3jX*o7#L7cBs8y;P-%G'
    '22Fa#(2_)+p(cn-;aY2~&II)4WRPJfTQ`Yx%xZlviFAmFA%>9H(ookCBti;j$k7<J3W)&?A>eaQD@T1!eeDxM5tVFEC-0l(_TO1~Pv6Heu{T`do#;=O)(sWU'
    '*F73~f)l305zLv=8=DM2txo)3Fp;8^yX!m_8l>{uQtSWL*_J92;ZBnrj<R4|r!sRUmh>6_#THBmb^$pK^h(#3@6(^2OYB>fKkd9XyM{ZMaPXAMl&yGl1z|!h'
    '5C|`#9tnoGAW$MmBFTv7HX?`2hA0+V!Cb&j#H_Vva$&On4VRYKr&hm+zF1jgj^5V^&{-a+Q|Osl5G%WS$WBq{&UhsjtK^IFpqo2{+L(NrL8Jcthsu=Xr(82?'
    '#!FZk2%K3VfM$JB;wxvZEQzBjiKkid7Fa#LW_g^Ap8mp6n-x1%5_+>n2u{ISGKn(1Z<gFqUx2~yX)W%Yl=5UP4{P?aKK$qFt%tBF2fZnIm%>SJMg0-T^YwQ<'
    '#7v&|MhGRF)w2ugIBP61kz{=_yvX1J>1R=fSir^+`e-(MHyrmy(M5*vv%~oXdPN_cUqF37VX$#@^zUp|ohy2?8NI-^7f|OZ9*<duw!L{&Q|jC1?rw~#vm30P'
    'P>AL*qgnrofZB9){PgN{H0(#@#wzfO<YzGPiph0+iU6p1)04wDR!y%dNhX>3H>0=bct_!v49qy3i_VJBq*VtHKNp)zqJQjc!?2FGABazF9UoJtGfg=e-I1p8'
    'd@>vU8=gGeBR2=T8Tc_aZK;gEJ)Unh0@L&B3^oD#>-xjI0p112gscq^jtO;_fI)9)bT=^Mp~%<B?*La+lbKXI_}fSaVhEscbei2x@S;TQ;Xd5*SG+y;Q2)(%'
    '#63(Y#T#gk9#NZo)yyXI4EO{+Vr+tPxU1FRRiLXFeyDkpeTD#=6Ew(>c^&IOwVdE2yo0gBF6<ryZ!Q++R4my1?Ag)r^M4(^>OOgK^y)Bu=s!L@d2;aL;LYLF'
    '6k}W5cQ2nGA0HiCFP^_Se0h@AstoK=O{$FP0e=`c5BNbq9`N78Uw*+~&tLos|3NTg%BVm!p`!gH{ZwU5bG22I!h|1EjgzX;^5aXXLpP_3S^8<e5~ov8)Tqy~'
    'By~qa?d$(lU3&tSbcZH`(cKgPe=MkG1s*##h;SuP%7yKxUP;eOCzt{Pcoxz0o_^B5nINV_vhn0}iL`Ncmb8)3BiUT;L$twk@h|<v&^YtRn4`Hl*e1U~n<t0B'
    'o2K2__Jb~;`%HUm(|4LR?q-))y%8CO=L!2WC|(;5OhQK^rMGQ<+e!FWvo60~pK@d~ZpQ5@vHsOg{Fu`w+0W9HYSq6@0TwK*66%55d742-XAJE1BD2Fy=c#Qj'
    'r+T2JJ??VqduLSndDQ|qQx4^N*!GYdcqM2V-ht>-)iU%7bDZ~!bZUwpKWMpC<Mr8ybCd0TmF}?A2+VKzO#pIN^V5&h%}2ZLR3mX^HJy{i0j{@HMS6&V`n#Pp'
    'ZFqpllD;69*Fk|a%~Ol=unP>7OmZn8?POo{T?^6iDe5~_@c0x%-H10#Dg-JSr>U3ALG^bl&|#fX%#hZSrkWv?eKU7>fQxr2W`zLG=h1eHG#hXeW@GFAMJ6zO'
    '*CH!)J)B%IfU~(lDWM?ToN%?nw|ukpCl?nJ4xmxaplB{(mTH2DABYPWa?5bPXK+se`+#@lDC-S=u$hLN;dn5)iE6vdn#5W^G56{@n~X*i#8c!p;g+NiTGsFs'
    'J12PpKn{{tsb{@&XdC-?H8%kNIP8?BkQSkezpL>c{-?`)ssC0USIxrXQ`@7;Dy1RiWI4%|$pon6X$C%pgS7@t!7si^u}$^$MpOB9$#%>)4s4H0%a|jo0zuLo'
    '5mGiR$5lIz2{TAu@Q-RoWn#G*r`{>AHxua|o><*?@_+giLIATSkmp@`m$ZG*9)sraICYV$(zJ^5S=B`Y^G+dlp{-ta(xx57mIh<k+Rpt{bh=F+IaPhiDf(~@'
    'Fn=cyUJU~;$KIvf{MCNih^z+a@TzQlbNl1{wAsqz6!9%95cdKZT&Iqh-y66{c2!O{s0QdopmKsQW<^6S=W@ni$Z1KK-s98{(yP+@YNyloy@r*PIKHj1zCkZ_'
    'Zkb^f)0E~*t1-AQxos5NI@64#jEn5z6w%2fjf~JOp+!O^73B4Rh)+T}cBprVZFU>gh|nO7BlRS@u%gEjicv_bxRl*;4J$<;SzC~bTkNCLW4d*AHN$XPL%$Sp'
    'L*l~3+*vi8D6=%7kT5uqDorW=+}K4`Xnu`Xs%vA{tqT?Uv7$IeyY7-8`$C(Kds83`4xMumZ^M+zsh1exQi_^r0>)gkz-rrcElz~6IRzAbi<wzT*^kj~0nbpC'
    '-Lb2#`xkGu1kZe0q-<1kVVG(PdlW@XONXLZ*MW5n?475Uguv=RdY34Vw5rGfReic)UC$p=Ru_@~PVDct?9)8&fs~#Wm5ukDH;Oi<=Pvw_tWjQ+um@_fOsHZR'
    '-R3ikQfKsy>UIhlSs4JiX$Met!hNMmoxQZIpGDr{#m?fyL8K-U!1V)Pde!fhZfs9#DA*3Z2RP!5dQRZ`sWA6kan1|et6b0EC;p%XRE6b&R=bnvUDs+P)e#Wb'
    'QMDCNQzXoAwa72rVXx@XXRp^V4R9OTBCzt>{;EQ-CzkR2r1+mbB@fAHJ88ov@1%u%7+nmpt_T&6Eu`4QtlnT`6yqbR^eLI3GVqOp;@zBZ@I@t;4U7_u3f2uc'
    'vABgI20U!9;WVoC2u?#^XS84AJ@{`A4M&l@<_brm?}TzUn9>_>pVM2T9u+MkbQwwxdbgW_b@B0p^1x?H#AsV9p!EPi?-4{4UL#}a$<FdBWcQ&};eFRhL&`3S'
    'ROy}0Ym9qKjmLHV0Zqm6eq(c&h1<Z_kKGmo7QlTNFdSPO7Z@JgWxO?@k9fS7b;qY_zV1CxKks6Y3DTyskH>@FY>>K{+%0+l1lY~gPNd{Rat)I2H3tqQ<X+gW'
    'RVfDWWccr_nlu}6QmfKgd!5am_HL^Q@B{G3P7II5sN6;G<4d|^j|dPJzIX#)QZ1bvy`m1&dTccx?9<`ffAHvms2^5P;FK(aMK`>evgxH>*!=><s@0crDSb(I'
    '40)p7?3M0j-TGc=^$l4I3@k^x+=fCGI^@)<@=jY(aejq2qkU63F_K%&-TlG~5w}H4*ImM7enHnoHDD{_i+O=~)v+n%9Nmeq9Mb7M>#@2XJE;M0Q01Iy^1$!!'
    'G|JFL3v{5jSj=kn(37e**j175jDzMq&$O4?waeSI%&=FfRDQ<m?P^9=z;`o*wHLXJ?@h9_MDr0$S=76p3=s?B20A^1n{(8I`|=z`F_dQ(bGX8^Id9%O%NDl;'
    '^$QcRn1`%-30>y94>zeJs2Fc<{g|`E;4|WmPDELc4@6ndpfSws<Kr{*otOuheacQK5T0rG^^1d7uMUs9z_V6`Qqg{>c32dU>$C011)YR{awVEeM9m%Qn^W8K'
    'M(M-Zqo#_UH`Pw^z3p=&T52yki_`cxDx5yWd`l~NRZTyB++@Es7Ts}dZ>lY>sNE+e4F8~J@qwihJ!R1<{WN6=n}p(4rMx(|Q>f8n88?swjM@;{Y??IejFpTR'
    '-FLB~Ro4Y9T2*6Z_=C9&DWSq6lP9crlI{ltZFh}(n5U9_YV={R*;^u!p2IzvXn{~@-w!`*?ZA~wH>`6A?F!s&hzFyK2P3c(Ef`7F!gpIc-=tgHtw31e{q8P_'
    '8AA<3KQObo-4=(s1QPYtXpshi<@VU(J4h|P=(o{vb}_j|hIf{+%Mko=c}1>t{T@Og&@vLy$;LoFP_f-xOfH7~sE?*yGQMw`+Ms(=G}~XnqK`z=1RVw1WvWJm'
    '9?7jp%6E>PQj`m;-3;cFq>ZPBzu^G<(0X^%9Hrq2iT5T#`_d8`5{Ljz+v-DOMoYdo&%~P5*+VmTYKL7eJ#uj?2o})CU4cvgjV2f2jECrymgcboP>F@j?z_H!'
    'LC?S2)CYCnqgu(6uS%YL)u1Pz%3b6;<psh%tC(4+8oMOIyv4=Fw?s7DS9EW2EGU);9ewW$*+JdKguaPexGKt=NCV7+Phydl=UAoJj_55G&~%cgDOCsCMpMC!'
    'W?5hLCk+tw<fXFR>UYgnM;}YqHP^mMfkjnBtIM}}R~$i*dBKIopMFv<Y?6HXxqjx5jPH@5h`?u^4L>6C222wk8j!?c$1QF(S=6dTy$C`3Nn6bP9i5H%rwJTw'
    'F(nAQg3KBcdr|sF*^sooI3+`1Q-B4b$7sf)V($}G8E_^Sn2zOry-BZe@#*jB6e<N4>E;|E2BtcD>v``Q#P@7E$`<4^BOTq$<$urTnNto6`lEVn>w9QSydU2i'
    'qSVyW1r#avXLdMI24cBtT*=7RbQKxHLPjv$xy_v&Ef?;FE(6Xxk_HS*PCgvltTc}wKO%V;L43%$5ySV|RV(j_b`t3%ZMH?|2bO23)E4U28s?^Db`{dVH_MDG'
    'T%zM&*tV6V;KH_xEWNOCs#2s16t7`sWW{S+s_M=j{n$Od8c<FW*fAxO=<>`3{Po^=`0jj>YRl->wvEJ?)@nNmYAbf>-#f`J{k<E*1~m5{2W;|<plDm1e1FlK'
    '*63BjuasMdH8<FH%c_Z5>jYC@dD|v`Gfr#+7=nRSTRC_y3xv@M<D9n4Ex6eS5(kWNoH%HV(^&g)kAZ(qjngyXt2yXu@nemw#!UHS&KLZ@hf@nyOs}>=1k;$5'
    '!rB$=7Y*hJJXeB&xWv;u(!_~g7(N}<Ot4vHpX@P3O-2(~T>5H|jfTj9vGcTMsA*|por`w10C_Iu5#t2ZxgOs7LI>^qY7+lUpGEATLVrI7F1(JD=k;&%x;Fy0'
    'uNKE)E_%L53oas6v&xT0M<Z20)9gc)a{Br+UXL@{MHY_-<di=%T%WH`t*6+B!js7VDLaf)xP2#c*g5SmrPSj9y5h3tQfbFtcG8Y_S6+P8c)Uj+%I9nC0puC+'
    'D{sa3aWkmf!1RjE=NnBd!N^F%<WdEW>!54(-Q{EKiWW#klBM#dr~0eV>?&;#$5?eq4+1<CTVtC^sOSF1ahWM~D|1y{UISJ=mKLP24=kr@&zofBju$(wUYffY'
    '(L|K9^)73w+`iDzwx>*BM#=Lv3~Z+MfQ9X|ugf;eqZD*StZ~{%f(xC0u0Zs?#{$C>s);thS#LCQK2!R%kSR@euQ*qcvd`Vnz8M$q4K5%-)M#^(CvXi0u1IHz'
    'l_E^jVE2GL)>Sn-t<p`eX8||9`e>^Yv^SSjV`eOGoAGRn|4nwAgxSYu(9b7uhrEOn3(t$pIW2XjbHaf>)d3xqekZyNksu27+`(1w_9mHCtg|HEeg%ason+_)'
    '8Wp)ARplyj9!W?=ZfajeMb5bT(e=&_8*krT;Vg@w38EnBzqgvn))vTyqB_TC^{s6*>((<mS(6zuGW2a!JN)PCdUJOtj&3Gbqd_#dx|l{P_rRNTRg9gatUw5|'
    '9%J_KK{oG$jN9kH(hUak8_+r-pw6R5reE8e(TT)^EXX)Mnjq8{0s=BLwd9Y4^}ZzzQd`5(1E+39Ye?JTTdIO(KmrySyGNf<5DQ!5F|gwGFWqNHCvVa=9~3$!'
    '<m_W+Tr+N@M}WhIX)0^iafd-1yT3yXza5{XHJIaQYb&NlDwcvH3L+;$AW|U|k;ExPDiDCbMR1g-2frhMz+VT)zdV1H)*o<hm0bZ1L$nNHmP3~d{fIAV=aKB<'
    'R>K%1ZoBGjKnolc%6+$I1yrQwKwWyMmfANXQIA1Jee|G2NH2$r^W^q8EV-x6#+^k)n*r^vBXp>oy0pzb(P=E&lGENhc5@Ax7pTOT6U@IeJI=^sxoWSaTE_dK'
    'uu%P(I&k$zkLr2{8P=Yv+fN%|E}op>JoT1xhufnt!n7UmgcZmk;rdT(>2tVfu?wp0!-~R`15S?#U{f<bFFzcX-n(4frj#_7Mv%}a9@6OIHtf2JMh)e&E2mRq'
    '!R38xVH<6=Xsk-ER$3k^0Ik@U8+WIk!edvnswdh-qsBwSA)hdR*52K~zv)H%IJ}Du0ciW@pE>u?d&9BA2BMf-eZ07_WgI+rZ$lNfxcDw!It~?Cfu~nybRoTK'
    '^7H?-ZY(V|?t%$(Xi%P`39W3-b{{gnyK7|g8M?|GAEBaV34EKJ#8l8CBL2;W@KloU<h}c%G<uY)F8hedC(wvSmpURv)q($+!tI?!c(V8kAVy#NstvLQ8{?=m'
    's>Ofo?EFp}2eBmXerr=T$A?G9PY;i~zi{pyu?ebol7NR!1Wn>Bqh4yi!pM1w{Z1)KI6b!HpW($6s3Q`f8D&#K01jT3p$YVnWkS6>CvntT_avJ3X1$BK5sKMm'
    'HK(sH`p#>E9#W=J<!DS#5ZLZRONJZELE*V2FItXcMAr7;<%v>OShn>K*xsT~Sx;R1h;Y`_N>w9g=CP&`GKcO+?vICfL6s}GTPf52&`}IHy>@9CmvKk0_Mi~m'
    '?nRae`_To7nP#t%@P$h6_%C|pu0o|!Ii}EV*DO5EW_5H%iGH9z$$F#rJx&wtb{v|eBvaYZYov^Wk4XEM4Pvp<9A_L#P@842wpSVTO#Kagi%o13^k3~+97?>W'
    '@i5xrFV7>3lgRpwb#(TyN-Rj582%;K{N+`4m6^0Rdg2gU#d<(>Sd4*%$O5-I-fdhFqpDcH5!fqsaxx%DahpM;@!y_BnF0YhyH;KUpmM`V-P2CU>N|n@b%FLU'
    '4AH{s_8@2;wl54p<S091gP*7OaRK-PUTcK0qVX?^^0InY0e#dcM3EX3&Ie8+jE&%P34>`u2ux#Zs4T=eRdEC$+F-p-bJ<`PZhrMR+HEwT*#J5RNnwM+6<xln'
    'v?t(u9#U|vW;O#rIePaI`a24H4XBR<TZ>n+V41l0Je7LQXEd2M$>t{*V?|MAnpngIK+GyIO{=4#>d%MAZ=Sz+{;$L1YP?cs94-6uK5-7QvVIi;mFUeBbhVIP'
    ';klR_cTIWP)K7z(gDu{?KP;D=)i=f^9c7u8;4)vD4is;P$yDV|W-S6#8YT+Ur8|arJ|L>lA1A*xZ^>dL7-y3AO8TmWR3cuKIKB=ilgKyLu#xg0iqTGKh>xRY'
    'E7DPc1>kCBIKyri(t=TMSUsyt&-Sc#>%n$;GVmbt(CmE@gl{9aAyvrPYFgcPO@t8t+w8bZ!5Mk9ATtHGc+KYn{F|RcJRUv76f1qW`_X`kLLz!!kdUbY1~F+H'
    'hj*!9ios+&L97_&hXu}iG0f)LdF+iUMVW6#I?VdKM{Z%g`S}lh5k?5AWPzIH#U3#m)VQz(z&;HIn@TZ(-Ar{xMHpaL_tARJW-JquYy7qFZg&|qE~IbBU~=^p'
    'Zb~agH+WmpkWyXFgQ9~W(vENjv^mcfu(Z9ak=ljrcE@<pL0SK*<$4$hky=u&u4j>Ki9U4J36ZmB4;#UZ6plW`>C$Hp8z4Bxej9)8L_4Fhr%-)~`37SR?Wl%8'
    'M~XNY`i017*5ocGi{1!XjLk+K9U;-}k^V@xotFzNoLByk{V~)h{$)m@ALZJC0xbMH8EIr<xtO{e^0RRP3_Wr!_U6Gg3fwYkQKyntNA;{ll?cM7xnjnFDu6l+'
    'XY<@%Hl%dfCMMNN5@E(9Ptw6YB+@{lwky&%rof+9O&+d3^;C11!!{{<w`TPs*>T?jgH+4g1BT`_06>hZPROTFhRS*_qqHYCa_>}zSbXhV983b-3qxdnJ6EY2'
    'zN`~%E_FFGaCBR(s8Ba<CsT2AjZBiLhHvCl#1fX4OPbNK{OLKZAKb!*{b$x+Nl(hp!%WXa(Z;zWFXgfn23e!`DCW42xV`sodxlia+wVK>FSma9GANB~A(!<Y'
    'cE%9@c+isZ+H~u^PcLv5-rI@Lf#rdRrhZ{BxT@eHVX!xGuqNEwwk8y#QR0VQNmRmEkdI2yuXHhd!d&%>R^a3`JX$Hxkeazlr^aGmR<9YLI>Dqqyha_p|KYgk'
    'zO2Yv$>u~*gj8L+%A-pqD!{k=qpJ^v5lFB%yu3Q@!oK59DcOkH!L9eO`>~U>RqXU!83C`GbeCER$!2Ul5WU?dKDgq9>GK-vImU7L*5d1`23<g&wkbEJ{M2Bg'
    'oShkJ&0kdlB#pf*5@PTjWy;Lob$!lBDPwO9DN!-E?lz1s)Ol-pcht367h+WM*C_}Tv``yx-S4*4qFwtdhF^QQC+2l=3I_eXRlImJNVP}<XirI>LM9bU+1sw>'
    ')x1@fjP}Y3z9VNWEJuyjsZ9-U<)Liu;WKmI^uiP(Kv7d11NM%1aZ7PazCu>UYs;<4PloN<a5=wQ7&U+uw3e;cgOot2PIOEj;D^dEh56VeOqY?xqy_{EAU={f'
    'SQ}tWql?jte1g^h*ccThn6V<P5r+-x-Z9mmwl}Pu>MxkTk7t6`g0OpYLG^_G-sH)vksD^-RDo<@U|Sf3kyZgDd5(MWbEU+~5nl7>K-r;+QC<Tp;o`kom9p_D'
    'h5xZn3xcZDdp98eM(5dV5Z%o1G6!PMcRC1w21-GoKB2bgY=}^u=M##w!d5_RMrZZ`$Bo9+g1B#dsRPK9pMOa|RWS<`T<++!M`r>AF?{qc%jTJRH0a&V;aBZp'
    '5;dE6vx;?ykQvZ0gsw-^TdG%NIH>!{(c5ZE;ZvSGJ3M?1KiPYvN||xtC&FWXrtePP9NV8s1`F#;^F)1&`6%S;CpaJS?M|bizuLvWrTliIAx#|~K83=p#cVYj'
    '8r`zB)zAQ!@Tr4w3FR6JNVN4()ntXx{%-tS5XfG9S%&=&{0HVYpuYt1p8h_aOyn=^>ylJ4=`H;+$odHGH1IrN#@P)=*48}h+9wJ(Vt^Cz_+yL{Mq;kEK7CHA'
    'gv~C0_C^{1g-v#`*IrW#xIIx89gYW#DwOok-l<k`qog*7sRlcg1NrV<T2pwc`W=z#ngf$+-U&N49DN|mKPUgPkyjHR4%J6C^;3cw{~sI#qHxj1U~m4jcTC#G'
    '6Fvj6PIN=r(eMZM<#DP@f?P`Z$<Vb<c{|Xq^P9nEZX@QXaWnW^SHZpVE8&gn_mvN)=_|~$R}bZs#u1QM73^QAYIE|J^w3EetT)Tq@U*5y%3gAsHj`#B925%S'
    '>(ivSaq5y@t2R^{+Tm9sb6TP2Zb)dJozVDyMV>(@)ue9xx$=@Smm?MOB%x0#qNcSpfLH=-T7_Z6iRu}g)X#|{jTK#N)82fpw50R%l)+axoJS%f;ysGaXlyq2'
    '&WAIY0-PP4hrLSAB-#>v`=KMs=NWT=&r^l}>S2ZHwC#i!<|MW#hT|7WbQ17znoQG)lRt#46%JIMM$&8f0>b=!0|xl;d-Sd{K3JUTfZeeabm4@<^W*q?o+`_E'
    'O1-j0Y1IjnV$AOfPVPpkoBLiaAXDRRqfuC;QgSY-vsT#Gjb?G>c(tw2TP$YkY?k!)#lfqmRjHx|1slm0{tNEdM%>1!-%5D$Y2#p=WhYb>hkkK2LMmtz#=Jj$'
    'Zy;RVItTX{f`HD=lhG)f<)Sj}TPYlw2|GPiUY>iHHn=cIGf!D4%kZ9Z#B}M!o{$H}#d6Q`lT`2cB-sv>i9S0PULSUeixOC$ld?60+2@==3jB71!1u;<mgyG|'
    '1!z2*rDK={WxHu^>a@kkJka!2=Q<USiOH=^&u{0$KBADI_cY3n((F6J2yoyv828wT|8e3-7L#;}c!X8=>@OzDJD2Nh@qgNjNym1xROfmz!Q)Ven%G_10hxO@'
    'S&-u;yuDliNlZ*#@t*m+o<c#V6Y%?SBd-%lv8J=x<N~T%Ok#y~BditYtxCOzN|BF#_)aq_!K-3>+q&+~H>r6F{ZmjohC}OYm@fNMtleByzydSoIY<cywUWyg'
    'D}7ZEyt+YCJFmvK(blHkCH3h976`=S)A?e!xFP}W^fpramN$A-<I{bf;WNXZ!5MC|q=9<V{S^M(Pwj`zPAKv;nEpkleDNSyeUh%cUW9<tv*x~`mHQUw*ZX)`'
    'bwMYs-E4SeqNs*f4qD`4pIg2k@Og?~wTjK>i`lR@5?}L=zBc`1g3m>V{*iNr=XB`4>4#1kRa@*5V53Ax8-&{c-EA!p!getU=PkClH{Lu6wG{7Lvx#asc1<lx'
    'V`(IIEeMgvaPc(x$3dykKk?ye(b^!{X#wdVve42?ohTyG3ecF4O~>jV%X=N`lHHrw^Yd-Ay&2t1U^!+go;*@H;-VVI5=TEol+F(RYqBl!gp0%|DbvLELAA}('
    'wtadFBI4~L!H9S(*xL;lPri4e#HBd<y?^@P&eR8-C|1&2M@lXQRQ0B$qTZYI`&UznIWQV)1G<9aa&62qQb9V>z$iYr5ndehF-9d2#+cr`_?Y)^$jg3wom$tj'
    '0EM`4EY^EDW}htccrhLeUAv6KvWIea3TO2eW?-6Pmx7$H1eR+S4hy1dKWFd8uN;cy-%}{uNhuCJfLpUkw<bL$#k~+mu31IJ=fP-jkvFyUkD-T9VT&HO@ll7O'
    '2MSK30-7O0RAauQ-c0xpkuHO;;#OgW7?lhwL4E3}kmQ~<8AaccndNMDf%i5C{SzVeFKZpk93*P+eVXF9S!Sl$;4I~OqKH=TG=)i;tPIeF9Q&a9*Gc<zoK~J^'
    'Vo>m>MQli=1hfVpd){e=-zHLWAG;{;tST#@c15FP(ia>MMG6R|l2huqf@y|H{KibPYK&*L5lkpphF#>aQso&3al4udIP0M3LGb7*##B+Sc;zK#g&T+w@Lzha'
    'svy%BK8>B_B}E}!bcL&HE{LiG8T&k9j)N6~qrO$jRJ&!;JGw!>mH@};9;;?T42Lfx%*_?q{_-1Wh4oX@pQfQn3`{+Tf*TpZRAps;G`fzsIKgF6&i2`4kQ()N'
    '8yje=es(%~u~DVkX=7<E4e&Fa0TG1(YRR5^r4)wgr*{R0QraypSFW#WAFE2;n~hGQ{?sX0zm0Y_b#he+?2<ey$g@ktEry*+Vv_75P)zg)Bn)N@768U&j3{yF'
    'vlorCo5+bPWPYAkfR)?{+7e=qgQxkBOt2nVmRTzx%KQxpc>Jd;8Ol8S>l|7no2jxBYSZIzV4js~(~EFimS=NGMhNUt-byV^759ZB9GA^SUFF-%H9+4NSHC>d'
    '<~rlkA&fLvkBhvE@vUK}IgoF!c>U^Jz&cU9>)<@`n~-xY$Fge$6NjFm=!Q1CH6sImzf)kKrHJ}+JpJEoun(+y9jFho9ErBURK>cl)HOQgFd+C_4+BCO!F|P@'
    '7d$8mJT^$KV97NL97GJyW$OGk`p3?X5yBh{Pgx;BR-MUUcsA^F946dW=v!WE{urG=gPdJutFiR}*Z5m_b_>+$*IsWN{c<%%2k8&JckkeO0ZHzM{$!B-Fvk)f'
    'pujtP{{z0B4g0XUu4Y+%>)}?TKJSBMNwp!`0R|+VjV3otOeq*8QPGP`Fm&{l3NidaJQ)(cWIgjTW3W-`Pah7r1zWB+o}XdD7|cESkDUkX3cj6)M>l$5s~lU@'
    'PjW|uHWRE*%82f-&PY#~7;ADh>ti;Ut2sJqX0r=IC>~Ghlj#o^Fv1ITEk8q*;<UFopC>$c(uGnIZ@f+F8UavrkUhOZ(_SCu5z4p;O{H00G7h&J!Cx4XxqyQn'
    '^-d?0L^adcrJFj>>h|^y#Ta1;==BIey+{?MM{n*ngf>M#7{OT8YEZ;qIE0D>EaB7L6Hk6tHQ6Z=6{KV%;eO&@c9KK-;HQI=!!$>)G$G5d45GRA1Z^wi>$wWJ'
    'psz&VZ|>}<@Ncok?QaEvpR#wj`t!8i*&C*=v*y0_bsn8qa@h<!`X<p&{2Rr*5K+b~i|@&q4mX-XPfoitT2_*Z-{<=9zNioHLw$H3!smZqA7Yrknjp)?Gw<P<'
    '`u?3mU8BNslWKxt_sc;BVT-{DL2x75d!7*^-UE^!fVU8>;-221MuP*Se6~n3y5CLb%qRqJ6RjejKJO7}%R%p2ZM3Pr7S!i+{8Q4G<{2d=c$kJ-)QXztX}o7%'
    'wWm%J6t{!$awGNmI#c)q+!ML3PqkmE*WF9v&78^;Q@36QjkT8JTQMT6g>CxK4%6haV=W|9Tu(2Z#4Z=p#jV6+Fl9s9n0=fA)f_HHx6%B=kPJPi91}bpQUZAn'
    '4Ms;-xUV<u3V+QI;N~L`d?d#zBxFF;_-ZWlYcCqGC1-jCBF0a@{r&^m|8SCSFrMGOu1Va*jgsQ{Hk^n7_7;Hg)@diy@pNJ-$Hs_(iKdos()`|$oeG>_z9!t{'
    'R@v05$^sv`Nu}E0NwcUp2+=$Pf^Ffvl78ST`EwbH#h4teZMwb=5S=06AxA#gX88=D9}E@aUbmbfe9$LGvAz02T8Z;jJfVL@tq3S#v4PISTAbisfB~edf43E7'
    'bQVspZqXOcx%Bx|VA3E=Y&}Uh9qD*tnLkMYmfL@ql5RbJb?~D5<mlz=gC}oNXGnjct5{*(jz(oU2|dEAJ)6RV&BG7f!)245on?K(7q*dl3Oq`HN2eQLk11=;'
    '`=f}sYFM7wiQE_B$!TtveOte@eI-<{!<aiAj^!l{ySCDYuT@<Wu}uE$YBNu|q{lz$=NP+%OKd+t21Nm1Sxm|>Y)|tzCYxI_ts8G&)6n}4?n?W2o->L))=2RI'
    'WUu)2IlvBB18KeQgyHum#dd><HF(s`J1hadB$TH1gtB`09D#bVkxm@+MCJf|h$Y@bUQ{JE*Ri3OZfG2Z7alN)_Eop1?=R=Yo@NmLQdiV&cRj3B>q1!ap+E;3'
    'oSu97A69qWY>LPAcmh%=oX#HOR{Tn$esvBKc@J5gMejq#88FCOMtN2%kiUxwhCpJC<K9I!2fCkaA{5Fg8Z?FrG>G(~GmxIoqd#c4e}F{Gj2Fqfz<S|_K=Ky-'
    'b7=@lFR(^QsCxYfo{Tc~$suLH1j7P{1Hvc0g|1Q!<X#b>r(iaZH}8GQy8mc4yN9pd9RL1BkVeJ$y3z7Yqq|TZ<$(W}_ukjom%5fDvY{{0>q@@E(o3-{?{zb7'
    'NB`JrK05jJ`D=pD!9czF)w_4F5l}tyZ8L6BfrxzPU`H(`uwf>sv%ZncErZ@|ggy^gAO78ZlmO?mkdp9`B<YBtK6?L<lPNM+lqn0qEThee{13TQNOkjQYq!4j'
    '5Vp1?eOR3L76~VUL3IgL^#LRW+QApVegN@i)m4vM#){@wvuk)hr_2%q=``H4KxS}M93XKsA;<tsD>=O8V!Bf?bl`{%9#+>!D9$knG}K4o;&?s`7K6;yO>eFf'
    '*WALyW;6H(tEpMdbxm5XG>sZ@f;=J3@^DU*KM>R5>11%r)yas-w{{Qf!)Y9&Y6_ig=lr!@lCZ<>|A79Zx&4nW?jQuSJi#z@+yVsmxgFE_h4&s_SXYEWf(h%Y'
    'ELQZxRzlIIl6Llg|8_{IX5DMpk6lR<WX`qo*p56-Sa+OA;s<rKUG+Hb2NMidLEg90iK8EWh_-ed)&~m$?eWH}Eu+N0RrD69#QrPkAm^-s*WaXArJpRkHzQaF'
    '><YPtR*chmg?09oPTcV$x8=O$;EynuTM!t8{I?QzkFfg4?q%}|#iE6r(2z$<sh8~vIi6I4DS!&Buu;GaTfrnh6^uHHDy-hD6aho2VTKV|EGfpSJao<~2$@3*'
    'PzF0Aa~A;LA?G^j3oSB~Y!x|*dFzgGjYI@;o?g~rX;<_ysT2Xw1URrj|60o%k|XFeR2t^ye$I!s5{PljpW(8@$>*8BVU%cu3gA?Nce=sznhA5dQ+Mf&R>B&b'
    'pDEQI_lJ%-YtCo`Q2Z<M3U>WPJVAvXS2RzM-rxVotn<(3CsA{=*^1s`Zig4Wcab3ZVdgfv;%dM}?`(H(;QgqFj;HtB36K<^`nNB<TLYnc2!)^3aJTfQYqQ|b'
    '$f797J^CT4j?8AV${xPPOY5Qa?1-M!JO>s+j?vyQwkQH$p#uZEeyE)5k+wSU-p17p<ul4BOb|I!J|hp>{iwlzJdS>BKGd<r+HV?j89@V-@n}H-#%{VJR{3zs'
    'qeMsG<ohI<ljuL4_M+o#?si!=r0DxvQ6?mNo@CF2pg{^EviFw7apNGImACPE)MBW75m6oZl4_4+eE9Y0^Jf>f8)M=z-dgfe(BD$JV_`v=B82RvtkJ5H?|^M!'
    '@{+HBblWsXVmz!fdzbb4=XfdXfxP!lOz8dIn5-|%z7q36*q6Q8tqCC!PQlMzvuAv5QE&<;X^N~YO_7(TX^*2k)J?DAJh)-n>Kg81S!^0M#3j#tm-2Il$rNW-'
    '^#Kv%^Bl&xx3yI49G<=L1R+KW4<jxM>=t@6WgySevIqyLfXgL0p2G#Ga2C=7MZCbcaB~Oob@9>iH8T4k<Z49du5fTs>q6b3QR+ulnnq_!(T(tdVI$)ZEFR`9'
    'NY#)QA936EW(zMGh6<&Kct=h1%|_kEFW}fwBsrZoGaJZH?nNH0M#T=%=Bm%Kkb@rq&|quupJucXxn$V4z41EfHN$SvG%+fUe(voZw-SFq{DHd%@tN9&<Pm@k'
    'J9U21xDha?aLugP7DjX?54Ri2u_duAr&q(#;0F?BBfbNpnh<OPz(eAU;^sMN0YTz?`urEm+x>$DH9H*F%mz!mot2nrh0_$rA@E^)93ik3+A9mSYETVKea?B_'
    'P72B&*t0KHm_G%;&Ay)FP}?NRq=xK4(|bx-vHaspyHhBkh@&roEWO3h$6yzfYbS0vkSy9&SPGmdYZuBhe@EG_PG*YvlTUJJTXc@${?aG1#haSvDgGSTmb_t{'
    'U8(ROx&0vSOF#=7F=1z?Q3AFjYAnB-txkMT47!g2Qp~5jV{PRIZ!_qkoVMA7{wV9sl#`hO0kIjz^-)b2&K{9`)<xitu4$;(4*Haf!XF_Ff8^otM+n3p`AGZ`'
    'LGee$So~257{4_eKG${!NR-@`TndO16ph?!{@4G*zHwb8Bw148*O7^~P$oLgdV|~g34xKFpcB`@;2H=Asv`g2=;s*_1XSPS&sw)PxaQ2|Nko62sn=gYVmf%5'
    '7nteci=(4o;nBAI{Q3CkWke7<^5D%8`~;ao)p30E=J3fIO_bC}RIkbafX{y7dhJIizy0*)_~6N#?$g7c-ki8qa83~diFR`Rs1!fswHE1wKsp7Ga(Z);0AYo$'
    'Xo%CR^A6w-m9UL|C>b${XbDtFBf`<@P%_v5BI!-397+W^$JS2@J!S8=hEALGzC^OHB($}yqUFps+!wxdKa!moyo$bP{)06RvQv^>WO6NOv5J8T?0n328Rz9}'
    '`$3n!RW=*toiBKigq)N^-J6`9*_ogtb1FAn%<hHa(>L%NH(FiooIn<GvRjw#VBdbN6YC(X=5`Te9tNV(fHXe18s8*f_qO3D-FRnx`a_yzMESoY>^zO==sUm_'
    'BmG~7k^V6(I8TnScs=E{=RmJS!yPdCe<LmcNGCKmTxab>xlkDcE>%ybvx%f*NqL@V_|g+aRB>MPoGK(g^VFS0I{#)XseOiRGkEMJ`*fJ!1XPH{R63_`QqwOt'
    'BQ+Kao(+x9de>}Y7&@u4LV$?pfS)>;Bsou@D45u_6dyE%VKbL}c`k5wAz(}}gGCWiEA3ZlfSol64wHU6I|<J4k}aLz&cVdToFf|7V=4Ym^nIDGM0U}TBubc@'
    'K5o!l>T#3ATCZMTO^Cz`f3{PhDcw^5@+ea9<BdHD`(i42I+<`6O7f(A8ZOvX1^0Hs9xJ$IKPQo!IV}pLPKz2j(N$G1!^Z{#naxPpAfVxZ8U=%7<-W_KILA@l'
    '*#_#lt7M@n_EF1{um60AhYqc`wc4aOs;g+98j=f-u=UtcFGvrt5jzQm?UTL{nfz+lN;8-r#7nNC>5oNy0%4d7q(rm^DE{y?lq4WQ&lkKC(33gg^0C@CHVGEA'
    'b0{6hh*!Ij(vLl9qRu~EaldH(&FpA|ReXRc7I@M52hP*j*X;yT;b|~)YYF&7KsP;?NqihU{|<epX+b(HCrI5c#EC1%Kij4qsq4;SV))kEiv~I`#lTNUVJ6LD'
    'wA)q9VjIj?|Fz`O!`C#XVqJo`bTM7nP*;G<k1J`Z6h?f#Yl?W4LV$5a7i?BnF{j9|2A2pknj<}(D0*6OZp-dMbx+}l2@C&A2!OaBV!ssT^l(sEYpt+aH%kKI'
    '8m!s_X+1WeKE<QbFibpnszW`3es{DZEAmxTWP`@DA<k;XD-nAl7km)O*xsy`7)Vwb>!n<<Rsof#W$A9V9Te{fr)$Lcbu~}x>(RVfQJLcIDoX#)Re?Doa)JKK'
    '`<yni(Vh6UIkc^$#vl%LaTKrLmz<cPpr+Bl(dE|QY!{WHtwRe^6d2s{gWlUt)g7JZVY!mfze`q865>JYpZB&JUGk{y-o>|b**A2ebB(x~Nz?b7Rx<bH*VIrx'
    '*xWj3MQ>Du?2mQa=Fz{h*`)rq2TK;c7+zkX`z~(9+MDj1!{e76Zt>#q;P@+OCEq;QI>@Uf>8Y!~!>HaaWlTrXLcfIU7^YzHV5@gmm~yKle<D!%k4=Wbk$!lP'
    'GV1o=l%2lmb9l|NmD`{~gR~S-x}WDHRbdI~9LBo@3fhvJTf0^hY8*(B<^r{R8~sesIU|h39@qa3n@r#uCzHWEpQZ{yU}=Ss6%g@G%MFAeAx3d^lU)*wemD&^'
    '-)AVL1W<$Q#sWI0Z=(|g6hFO{L~ny^-d8TiIrWcS*Cq<5wH4*hP`f{&9ar%_l9pk<fNv=}Qq&fU^9(roz$ChCZ&8{hVw{|Aw_D9dr@+IJ>kEi3thc~rfwk(y'
    'McFs)quj2VW6NaQsUnb$sn2(bmFvNVdtA~E5sT`I?urJ+_^aF@tC6NvZW3#pt6e4cev!O>{`#=_AbNItIvWm-U|$d@0iGBFb)ZgQCf-4oI%U4X?SWnCzC3!0'
    'ZhO_k-fVRH<hDP`s_ND8!CPW7ZPd}AHKfsLw;nyfJ;)zE(f7_1xC9S=dU2><Ij)1;in^#i8MylCaGG_AkOL!&bD=f_dum3iTH~LT7Ie&%pf0A~Xw*36_^5h0'
    'vQZ7j7(QrO(yGF+s47XwFW{`4t>mPRz;qb|R`vq&AIBT*wn2eTRGQYNa>?=%W9oj}L3jDKq)wf+RaLv&NlIJOwKbjEEP*rkR{MVBV^tYQ&g}>h#@NCal0L*5'
    '<qG5wz66JZQAVy2Ao1VyMjz%B9TU}dlbsl&vM@@6Ej3YX3!edT!e5&<x<NKg6nZE0=F?WIU44s~Xq{x+{JCTP+=V}1zc_ehCase^z}K*wkE@-}fwX}buLY-?'
    'W(FJVXxBd)VBVXmprrIu&BGB#`A{xn^0bfeoMgQLMwO8#lgjo9(_g>M7WHwKp<2wH2D^7#kE|BAsBf-ku6>I9!g>zug~C`Lvrdf`_cT%PrwJ(+Fxp5u1x#9o'
    'fkg_SK&i`d$I1!>|KOJ4FNJBx8`<eQJUKj&SNe~q$49R<2x@3c{ChZ+v|2lllHG@~dN*Hji5n{~aU;LPFW>TwfFZdVY9phqA9uEs=;_4}*qLGU%joLggUNM_'
    'nc8Th6U1AFnOu5s&)uA7J-kk|D<!J|VcSq1#<51BU7XLd%-%n^Za4w58W=l9y!NB!rbFWR2wPW1;*mTb9gb?zR@&WdoKoNR6P}y=Bu*}Fa9`vX^`5rF@-6Xj'
    'Cwa6LC(w~xs-x9*1S(B%m9boOF`QG7sGjZb2G!_0_NZNHik$6ZE}=IRo${Pl_vq}&<fil{GF+;46DTO8rp;jXCpRfsQkGo+lXgpy6Ajj#5QM0swdXm5T8a2<'
    '?WsSTHd+a0CT81izc-r=5d>v11Zih-Gv?sh)5+DlbE;;Keox?Eh|zq582CV*?aEFwm@^4ilqf=S|4axiDni$5!FXohkx_QG5c^9%+YA$cEo)JBI%?!%)RR$%'
    'zub1dEF{1FXFK5r2`)C*UZ9Ib^l5vgQaia)ay`nH@yqY}<(+Fo#)URrWEgs`yxdkuj6J>8h~L~#n+=y|B>xg3cS`&x!^_z6h8!b2VqvD!0G>m@-jNuKFSeNG'
    '?20O(U>;3TmdSt(bmGLaB%*c$g?QUgMpEWhXCqZ=zLBbzaXR;#4Mswk2eB)(iHw-W)tpg9<F0`~6|=5&O+jJFtixJT9wHMa1$rP$`<g`M_=z0S0YaV;G<^KT'
    'BJ4zVm0}bV4ooq-m+m`ND@se2QZ+B9c!-K_cNl|F9F9%241NfI<9{sn-Ik7ASK8cLu`D1E9{F%g_!dsF#>6lNT?_*45`KFl_gHuWiV`kOnJlc^pewwau27f;'
    'ctZ!UOKb?WL=;w)E3I6L61%8^jptS!(#y~*QjGWomJbI3u*P%PO?F_ktK779{<_Ld**vnhXrW#Icq;G>$lpe$EQ(b&+uluQqp=vhQaZDZr^g&FGC$@Bsrgo3'
    ')yGE?6B!3oM%D&Il~HbwRh4DmQpsZ5w)a2&X2Ob}Der%l{0e)syR&Y0^xoEe(x63l8Xpw5xHlpI=i#O8ZtO1YM)0VtH!oIHgklE@x`ZtG?vDxZ>IMMOjW{EP'
    'ZW!~|j$SjICAC}INur(D(zDy{Pm~zG6N{l*G13Lv(D4^eem<XQ!JQxJI>tqcRcD=ol#A9WAM?#88kVD+y><y&=)CPLkLIUuooE?)k~=ZNa^;E$G6;smSA*v1'
    'g41K@HBCYR48WQpij?=6iuPmU7#G}9IqU_kXI>g{Nv-gksg>9|l=~!y_pk6l&=qP_vnNtsNuE9QhGHywk_&iK+r=HA`r>_TQl;R)+*B!6JYw<ng+Q6`;Wzq_'
    'stVme$5!bD7!@bs$wggpMie~l;zClZ{!D@*1rksQ_miU+FAkr)>Hd6p{O0+K=l=p8AD$|K9FHdP{Yk|8;$AvO31fJPmQ-gCgJQ)*3fZ$(Kab<F(s6NlmTIR2'
    'KtnU})-HNn3X>7+yVi2tp|?IGwY0y5H5Kq(T%j3YdCksoYLv~|JX?2~LQ$)^t7P3sygUpEJ5oFM8zUkzO;DPYFgcj_q3G3!_8;aU&|b~uVyN=D%X^Nsw&X?@'
    'lcN^P3k`*(_o?o^cwO^w>!#oF3UO-A?(z9<X9GI2n1cZDb?l2P$*il`7p)<#>Z<Zptc)+8A0Hnb*IzvU^)Pz!0uI3QpPwHdN43-JymvjsEj1q9?jZ)&EbF6`'
    'k6uZ$tama03U<bqzBfvLgjTw<AwyDK3~>W=N5c;p{iMC!9RPdd<Bvc^%6_PzM<+8{P`4Henv)Nnzj_4&FP!}^+CJ;Ju2_<TP3ZNQln}pcO!kMa_<zS)^*Uz@'
    '2(B#abeF`-$xI6~j^t^g6%>bmi$BD0W`nL4Qww*D!Jt;F*IT8%rmo`g%=JDGJWfSz?OVVRq(@#hT(tfL!w<}=wQMxE)E3HZyW!6?5~yDMB9`4Q?YF`?rBzGu'
    'l8?<+(p|i-B~=7j9o*#@Ps0l`mGv<zNuOnd-aP7F^t#rgrF7dZzWL<5Hypq0O>3sRiRqO2G+u?s<97;Q^Uv`yp`C_c?e(9ZAD_I5YVUwP4B{4sd7TXx1ams='
    '4QF$5_QqAH<5q}N4v+i40^a_#?cD*hjFihrtYRrpLaOQg>jM}KYENsGpN@Zf_2gOi<n_^;N)kCg(IdI?)4{KY$G-<(y?*|$f5CBkcJvxwpS(Oedh_i0AwP&e'
    '-@~n7*eN}zwS6KfyKX9KncU@4!Hm)savHR=N>|*h(u^;NoS=1}dAXI0Yi=L<-XaSXn@eTDLX0k#&sF9c5?amLa2SJrarbrl?D~6h`yM4(F+`=p<tkpFUNBn;'
    'g^>gZzQmxc7dKL|JX|VH{8)v~XC<uvp|-4yBn>Cxq(JsrEd<00S;^6Nb3hSGQI2M%OehSCPGUHsQE&`N{3YIlh4lUAbekylQp&ChS~T5^HL=d<x>OxMEG6q-'
    'iM9Xv#nIc>|3qM#>nuV^b5y4cRHLjnsFUrm20h4Ty^+h`>jX`}EcTGg$I6cJdn<9mj3EdWTpFzgxmQiEPDjJO-c^dPL8H&2H%}CDFA}C`Fzem$hQFFo%E9^7'
    'sX+FUS1FJP#I^3thKqBUaHtj|Fffr5;Q+ry7Zs_G#z!Dbr&%^uIAACZk0sy{-BdJ)_gQvBedZH{kFij79$j8d7F6LJb(ZKIGm`{U_!~ssAvp*4pf*^)L?!Bz'
    '{t{j{d_*nMbSNlb8Z$SD-b_~`6yYT~3S&hr&WDU31$4is^0Sa5H_OnfqtYT)DCuQx5pTRVM09YRNRZA(!+*nfvmU4H%*KOvIFFR;YSu%abCv6=HzojNwdD2r'
    'H0xuQG+O)3`@i0Q{-*&TsW7An(sV(Z#cNiBlHe~wAHhEkfBA)eKY#Hn{ujYY5O)*n!)@Mu`}`F`M;gZsn(LNq3xu5=5~0!?;|%Gr{`@6;E;%@zXKD24(IZnS'
    'E3)U4k<OjN^$QaG&2T(`^Mz|U8@_voZc%jDxY8Gg2T!}tkmcTrynf=oaW|5?LAZkd{oB!-Lm8>6!>WLGZUmc%jvEE65}Nmjz%}Y9wU6H|;HXl#9##k=B)B&m'
    '<^$a$#PE)KHv%S3mCXCI;gpcW*<Q?_J0805+hyC%K6cL#s+=O!KAPAy_?sq8TZ7?&C1h&v0Q`o<Rfi=q(141Is#Ge1hbpVVL`qEnhCvM{SA4Yiq+xUvQo?Fy'
    '6Fyc^^aODy5my!bS&7Spca2`_!Z~0yl;kwKRwYpFu8<5{e%eC$dh7+6v=ukfX;(B2Rg3_UO~l`R)I~Dd#osk)k@&ez;&dR+hxhA)=mswGR~$uA>A3O8`@pyO'
    '8Ci2WcRCw5SJx8OT$ehnLCBj88i(74Dvexgr#OJ0TFL9dVO=Y@uFyoy9zVxz$D|*GFFiR^?_BuU-kTLqgMjRtX#qLF-R4#Z4NagEtg^sb?>^`h_SS<Tw2wex'
    'w4;3jR@$ISQeYm~E=Do}>@!a&=)`$^iO}{`yG7%%R)`WI6ghbyB83>Xa-l;UIYfKX*^r-e6RxVmDSz}}$&Bm5?bgo2(3GnJ0qjSOJR3RGQMvwL99g5$Doi}8'
    'Aa6=UrSgxzOi=L!lr(yI@Xzki@zcZOlk#?ZqZxv!ts6X#-KwC~fTS`@hKWC~jTxghmJ%jcz?#Z!ca6tig#Tq>cvZ+<6Q)olND2gnlusIY<QAYdb3<)uM46HC'
    'YNjj3Y(gc>^fMK~P4;TOys%&NjoO#>$Yle7A|s?3oibTTL3*+9aaW-F>b2SjZj!OWofN(SNW@^<)Fm}e03or8FEm6?0wIDjBX&vws7NHV9>3=Itl_)Y19f5F'
    ';qI1p`_h=?a!@o*<(I2ngm8<{TH*pK^f!IY>E(4+o{&!hrQxD;UBResoRv!)K1?(|h@&59)#&e~-Ba9V9z@1C-wOm<Gl>*hE$;a^QP^k}Q;Ps<exrtVkst1&'
    '<7l8<8djEHJfJWkqLV|~DNuQ+p>C9dn_Vt$1?i>$SV)U{-gbcR_VfNS`5Bi8&*2#Tm$4UZMLPvFY;kL=-#oU2Sm~UW#VbTSHWz~0e6$<eU%|n<DJ659G2K<('
    '#P%!03h1!WcFWL<PC@>41o{6*_u0{J$DF8UH;I}L;GZAipN9$MF52Q$0{<YP=^_7V%Nz#J{(3b&37GxEYZ74UBC7Szuf~Yrqg5g;PG5R8MJevQH#$=(xG0?u'
    'cZR`83>cgv{sZ56F}%9q$X_McXHoxZHba#P%>w7v!^bSM4Mou)G`vvTV5F5*MUs19XKETf(p;8m<^JztXVzte|7L#j%#YR^EE$DCK2W@pg?zxb=6^k>^q*uo'
    '{`;5>BEA3pe8$jd`c`5aR^UspHJG>BcJ#gJM6^vw({|!NpIw3LSg|Xq^@7(!zjVR80(B^ECRhi*lsf(!m>n2Gc}Ub3+LC=7Xx9uZbk!m)B_2u4ML1=1l-mb-'
    'Ht57|q?BSwT0WGPs!b)y!P}b4a;y_eiI^7%{+261evxjrMU8#Vqy2=i)y)18mGT{x(@KXVdR^Py&^61ipuJx11?e*Pfy8dce?af9b^Qm>29&O#X}pKtn&uo%'
    'BGjEQLk}<St1mvV)SX#1>h#Un!Z>!XB<ORH$<1T4PKvG`>vjs<JkYqtKZd{8z&^%}Oh?H%dz{zAQrEYb7%sO>#D(E=iZd>+O0myyqmll<h2tr%la<u1b@bVv'
    '?`ao1GiQLoh3vzUmpUXsy({@6NIA<LL3b{(PW-yw2=L(&XM}rqM0k4e_7yrJ40<=?LdiR-A#&bU^zFmFNZb-A^={4^;hrthPhT4?1e_F1mK)1sQ9Hn&u4!{H'
    'HMa-+t#1$bJ7md($HkzPtvd<yj~?8I7_Wx@w;2Do82`5z|F;<bXNd7cSN|5{|EglVzU$f*b<5?g4sM~ZV|6IR_6|thDp@u3>#NGx>&VPSQ9OF?lqk9yGvSJR'
    'dZ6oydn#(8lqFftCA%A-fJ<K8MHlK=i6fSB7Duc*l30_nE=LR>F5!r~FD)jqiCiKa)aDlavmMJ@;T2!{yyAtmycgE;UW9qYi@z$b`0{UF@o!%7Z(i|lUhz-l'
    '6<_|%EB=*v#g~Q)xG3Zm-9mpIUh(CB0k8Pd=M`6DCR|?e<(Kk`7hlFJx*On&dBuwrdBuwyulUm96<^+!SA6;UPuHFTU-I<%>lOy()feYkeK4F70UTkhqd@pl'
    '6kYAlRGa?vlrGCi2PyJ14w`w$KUAm+|9X0O@bty=SLnU<fS)`$z|fNiJN(NDCxPECAAJhU)O0i?m_Yb@%84S(5rAhiSjyg<K@H$%h`ol#_sw2!?bz(~gGUXO'
    'UU!8ABLQkwWXH7_CEF;g=FQG5r;LoBDtO&jT5t)X)s$xpe!}!rpl|(58BuLVe`$G{k;cAo)n0HZ8rS9qX`tbR`lK<0Yiw_#!rr~5-2eFlWK(t?dUx0$8(DR>'
    'TU!b$?e21jwY+UTXB}@GitXZqSewHDV&&b;eX-e6ISFVFcNtPnXNd_?Ye6n6*31|s6{JbBvI<^h;!Vzr*$JeNq7K+a9`l}2XVDA(krktlnMcK5V;5nV(4NnS'
    'VYp@LB${14wpmjUKmBZJ*!6zY<nG}>q4@w~X4ofZ36tnyT$IN}qv1N;O(L_iJ>JK$1nNyv_qZB;2Wo28u2^&`zy}5Q-hLR4&t6t#hAh~<`;m~_zuF!yP6)h='
    'PhY;TRK6lc$C8bo4+XHrGAbIB7u>U<e!;*CB!hE~gQLu;826W`6_E32ZOcn!+P4aj|4?QN2fH~=0Gu5aTRP7LxE1eL*nQ>2Wg}Vir2y!rcwZV1nIM{gdot*T'
    'uPg(Y^FDG|0e@6Wg##rI{Pgte$^!*iAuU-T$NuYKD)#@2cp$r4W*Ho)Xd^J_nYgRKP|9R27Z}{t{bGRu>R3r&kaCv5pgWRSld`VB03ZI@0s}&izd(NrM4%nj'
    'PjNqxp9MuJ0CR~{7bEF^Fv0d(c=#HqZm;d2e-*;-2KwuOek`n1?F?$e$|BUZZ*9k_h_7V-XbZ+4ZOPbi;N$9_pS<xyNU$7+BlDM{YN5!omdcG{5G(q<K?d}#'
    'B{8+xbp~5#hl;~Bin=zKWPZA}<AiKCT<PIE_{ux=R4|WRhRXOQMHQ)or{2KsTjXi(crwoehVuzo4gR@`*<fX%NAvYT@kGbccNuq0m^-4g#!*d>kURyyT~>q~'
    'r=U`1s|^$sxRfOIt$?X0_zB)G4nB$xjN+gWU}Je40vy<wf-6-#wG1^JP_2*MXG<o7>Y0JD;0e+oJVBr$U;5%ef9z9x=tTNsj6VkW=Z;mPTMEYdyMg{{+U=<x'
    '5>%Dq*G1_%h{HkyX}gCcIy#a1w)iMz+N}qc)uP-nveHt+)}D%=K7V$sB*rOFFz_VJ#~lr09-Az+wQ}O}DjMyw6}87M3!|M&1MhriQ;&sSVwCIpsZVmL*}3bV'
    'SGJJ(PU(LsYuFbU2bUSHLd&_#awW6RQ2)zq1HJ3sa3lmeV3Baz<+3Z89Hv6hR<en4;r)DSf_%M9cP&Cn03dv*yi#3DdZh>L`cA8(WLWD7NwQoqiL#B&M#$dv'
    'pbTG>ab9wyJ3m~Woc<MFif5xqZ&B;cwtwu(+R;?WXHZd&{2_J1cvYg$h_0pwx}keoFJpTAj!13gJ+Vw+st2)?fOiSvXMP!Z(Xs7)nT<M3`))2D+=onLZQ6R;'
    'Jf?<9@^$`-pzjKlD`7Nw=jaq0%CKTzk6>}FXb35a=nfXOBwMU{In8E(ono4;O}`s~3cso?PUenMAsbWNKmT&Fw^;&Xds|V)aOxmdu|Uu^<G#CT?&BBQ=G={T'
    '57xPltD5IN=IwL;v<-Csyt9Sw&kt}odG`G9#nU>9wyo&w3Rsvk6}dkiUi3ykjF7D%BOSu26Av^TeW;`Si1`CYm}30C#qN`rl1Y)c*e6GCflu9Opz-JA+2P@9'
    '__a&FemOciIfP%^jmBsG?8U*Wr|jv51-9tl@FfY*@EV6nD7YlgyC}KOpB#3d93LLMEW*v@DnxTD8UY3J=VAZZSbqir&_D$m_&~Nm!XGA=h-%4I6wEJx>%t5Y'
    'ba3Yv<`Bc*A%h`2UMf8cdAysw&w=GC!0#=^?p30KORC4WHHO@E){Byrl9C@k{n}_$*pZxGKQsks!Co%=2lAU$D8E@n@|&p%rQ3^^I}ixV88^Hs#c%YZRXqQS'
    '^#qq!y#cMKB-QfP3}4TB<AuL&{oedsGg#)k3%JE@Im{VK>kw2nE~qApjVQ7RlT{e4wIUBmv`9&yEab&<9#Q-^&b7<+qDkccG<U7PO(aSDUm0;9#zV$A+XNPz'
    '^-6b;4UrDmgIx*9vL=o*F{3ycpC1Vj@xNca`Z+!JI3cI|uuG=h??=_Ix~i*SM4O<nLTh0)2u+@Vqv)wj;%0He_E)IkQl%Fad_=K$932#s*lqJgJ!}smLzFGq'
    '8Axja-QHk9R&5re?lx`oPUvGlLephMHv2%>4LL<-;8I}B-O(;s`_aqJ53A4Jd-T~+*KO~1Wf|2?!_EyOKYQY}!jY~Aa$eg$2DcXsiw`M3sYE*{GjQ==qh~A&'
    'B6pN)ik!$#8!IrBFt6JF1qk5;CZ<5JNf$+<fTVA+PTMWE7;ZG#_>Lgo=qLtl1o)zcE2|z#GZ1a(K?Rk7MCFpiAN4-^acnK{=6snCQ2y{PK<qiGR){lXD)Y#o'
    'S^?jFcaOfPf$&|(*&-ibx)!{aq>0l=b^l##Sjb+rYRcQ-h6TG|3=v$*OIw<x=FrptZ9iRgx&b`HCkot%mBFr(oL7~gCf6tG`Bw~lND++--lr)uA`_iXO|yRB'
    'zFaL@csP@Nz)FkN5*<;u@RUA524Ss?f8(!gIiXd&TIMaWr;;JHKWc0bY6+isqW;fhPd)QGTyI0v>WY_oWcQUWH)7xI!lk=`9xPfy9gQSQ$!7_cx+AGIDZ7f5'
    'P_U6y8U23HkN!pKtT#YS^RF<p=qz8Z+KYTShr#3=@*9Q2R`&Yy8`cWtvoh<w=sxEk+h=8YnM5qe$$S7MSggu&#<MZ`dY%>7FQ_4V`{7f~_NAYHKlyw_@?8A('
    'ghMYX1fl+BNTR-w-(l=nD*VsC-W(rc?JtqTaeW^@yklJ^eQF8oF2-K5cRaE(r0*##1AgwSgdDAbtPE%Cb2t&%7mR^vQYGXMB>a$eNUi-zxB#W_N{VH-{GcT_'
    'ti*5wiGU6#W>&87AN1FkMi<3b40og51AdUDAy<B<l<AZs2b@yDQz_DBJ}4TDi(*E?KKol=uEZaF!7&XelX2Zgyh}$XMW)Vcxj)YrSL+p>vSmxUNj8w!3+D+0'
    'dr4ubOvPRI1AG)lfk$<*OI6W#==MjRzAxq8VxI5C+{6}@3G?m$pd+a08*r)3bz#T63Ex%?#d<XUH1x7c*b$^lzAUcUMIZ>GbN^qlE9`CNhgAih8-lk?qZa;>'
    'veg2RbpnQ!I4jcpS-GBmSyfeIMkiJ}Fxk_L#TK59mAB>U&ZaYw%6}G|tgva>Mh_7kaVKkP<NMvlt|@F&B!}EPl~C4!cMeGzo`<f9c0*IStwov^zeO3OIPYX&'
    'NF^I=i1~OizFLwS{)2;W8GquIOk926-DTgFR&GQ`f0;%%bQHI%1CvDgO8%h@0XkAMSLxIUC2AtedDT>D=&(Nu-uGC$QW;pIX%QWVE6R4I*I&pq2EZmO@gWyB'
    'hS}4Cy<GFWT~PehjMH1J&r)GSQ<>z%G{Nm^J8dKhQWR-@;6@9v`UU?;wOq(i#9qisp@9^}xnjyG)j5O}e=;h3qukHMh_++S)`ZPY@56s&M^X&~A%@GX=a2i~'
    'qAI9`lYfgWChmJhGt7HfVZ<T5lqU&617v}2&%ghSaE-DeP3&Gkad$>6!JS+xl+q+vyVUL`;|J;>{i%<#T~XCkH6-KsRWo+6$6m=oaE5Zwu-deHwhA6r*R0!R'
    'tnZ!y;}q=M72DT{BUTX7paVTK3p$3Vnl2PW)Wi%3<>^IIKUo_~B?a_l4Z8N5j2scD*F`0?c=+HRa!X~u)drtzAhi$`V6jClwkxiv43@lNI*^)$cI1@`(ns{K'
    '>TeoOSjj8T`_a+oKMuN`=mI2+0z*eFqUjprQnfJLarb3(n#0dr_Ed=_*%79B>Xpl4&P&X(!RSwlW#tFxrNT`FZ`1Pbhs0`R=eUYti%1DHO?V=xw1`=0L0Qhn'
    '-^2i(ED#PF`Kr`0P3-yYJ72@gk^8Qi!%_iDwLve3CKu2vq0RB)gqXXXkwTWot~$a~B~3U&xYn-4j9Af%ksD9?A^NJcHuSy=)h-nH8pO-@M<28IpN4TZnZd$k'
    '6vR6oxf4mMomf;mY2;2aSLcMtH8K@+6$=m56qsRiG7lJ62=?9e)Hki#Zfs_&o0yu+3BpDE44f_$?YSkJMTQ?^TH2dl_f^JiWUxzG{AY?gCUImriB<-?2;bR#'
    'eBRAY-v9B}pKQSYiQ2%v7}p8$Z3zr#fo(!kQW41}SLZJB=TP;1?6aQ1q~f0ve$w{XIvbi+9!4wlWj}~`YViXX4f3GbApP4JRU>I)H!53-kdu+9ur5)da_l?!'
    '<}pq%pfEjFYDui*G>TcR5hv<_&J6{ISLnB(ZWXM!Gp&A%l?Q}?T4@bXOI?+l#x;>V&nN>fAk@<CCb*#_CgMN}1H(cpuov}!VgPYOTE|&}uZ&0-!E7`YtY?s|'
    '#VI24sEtwc66dB^GC=?Un(;^2u`4VOJ74$(V=lDRK#7W7qfCNh8{wVy3sk!F4#+vfc(EEN-wid-mM(7<OZe6qm}*I&=iAE|9e&)x8ZEe)0nQVu`Se7qA6F&z'
    'LgZ<54SZeRX4w89V5+9C6i7pg<L5T#<JA}G1nr(t8r6+9mHA7FAMzp(=>KW-^y%eoGVIjEM!n8&e`=#hOr&AiMai}<$R?8~V=ODr=&V8Kf_n~2)a)as4RkX@'
    '2UhbDn{pa6vC2Cwn`gy@4Fp9UdcVn;h>0|)u%fu!F{6i|IO1{=x~ZnEmGSNde&X<+RLEbdRr8u$B{aV&>~B_Vy5bm*v>$}`%wYyRQ5{%cBKY#%?T;G3O=lt='
    'gf$5&G1xSy$wiwwiv>5W4x|od+6p;ME4yOO7mPVOy=aE8V2LU%SZW(^c6wF732B=!Bj<SikJoRt9|1~nLF#0^vJ@!en;Zf7k{;E`S{uP8WD-POTjW<Tf5r7w'
    '^KSdG5LtesZj3F#WBSHpbD85ZwCLM0wS|p_zcKDpgV1}<N*hA9k)vw1E+2x<b$;o-vf242%k>^nV0zPY@RCm;{bIlMo#66{+Z|6SxyNC@x&|B~B5ejoH)GMj'
    '<Bo~B4V<X^LZk?P#*)Tw9RdhJ>h&j;beXyPZj=*@ETT5$ePj{6dH?saNHZ__W<Fet)sSeSPgURfs)#1$(b$XLL9LLm>DE52l}hSfycqSC^Xesp6@A|WwLRQT'
    'Akfr-X>L8eFh%|r{d=9SF=#UoTtKUM1BR*(3f?Wsq(w0;t}(#v<V$|Op5=$A?SbXaRj}KuXjPW`p?)|=^FP=Uj#|+tc}X0P_UZa<*-Dg}D&=!bB{n?!{#j@8'
    '@uXR@*BGCXta3MZuH?g_C7drf{J@L(X^}RMfmxgk`@Ip%FFZN`85N0Grm$wbKYVT8aI`@jy|<f$nxmj6BLMv7V%K-59BKHLR)-uRTAUlKzUhY_X1BFX3&S}T'
    'vA=OMViiF+N_GE=ZP$R(2~8LFtxcI5V^Kq-VhsTpX~E~Am&4!!odpD-R<}b&P&Bo?rpzUKoqA@)xn<$|n|w3S#jYJZ7RgGo#XW=V^`%dtt(WuhA_pl1unYEH'
    'FQGhza(|bw%P_t=NeVY-N#GU^0nYeHuM>@ZII3uKLz+DcN{9H4UK$&M1#!RTsiBMZa=mJVxvdr-h`FIAg}D_v@G-Y!aWJ>;K<Z$F2AEs5vLohxcl7ZX5an`w'
    'mAA>B5S6Pio~yY`Xp06|UPQeYub#)t=;+zA1C71k9s5u2rv@d%-$0zFe9H?T&V&2oM%TO<6nk7l`=9EXcB^(6;|EzL+KR@D#bb!hZ?xhreVf?^K5SFVQn(Ut'
    '2D{VZQ;o#FYHnSSEP=xa1)W*1hWOL4SdB*PdxrRfmmGK#>`?M8bUXY8Pc<Mm_N7C(0<=dqO_lb96oPu251*(F?wG838F<%o4tsmFy{>K0400xQ4Db{@_RF?o'
    '|6yCRlkB}+JAUZXwduoNt~u-Q@ONudA>wKQyw_^e%44-->#f>xQ{t^^-;s2m97nCQ_4WA-Z3P6qe<^2qdonAR>qV}J^vN;6hfnB={9;jl&#zHw(6XLMnWt0U'
    'ODpvNOP*LcFR#eu%85n(@19T(GKW)(Tfy)7qJ$*YbW0ir)U8P)V+cu-H57xtlZI@gn4%78nP=3e$7de(oZ^0bLYx06zPgip08L(uxOqqJifz=cYjjQh6Zd6-'
    '?42K~#+zd4nB4Qqy4OwUe<sAR*zQj(6d{vuD+ftoYdLaVV=<wYZD5C$rc`HQxFIIm91*_*jxQ)#oL|UDlZpWWY@wym;whPjin=dMm^kHtnRDgjO_#RBprLBk'
    'XMTYkXwa{!tngypR?TB|SuOo|AjE8C{i<*pCw_aKJkhqDUZvEA5=gA<H!Xbp&1O0;c#+-hRa~FvUo9(AqqLN!LiUQ7+4pLKt!rCAtTfr`3cI|KyMo8ug2qLm'
    '+GMD-sa|%e-iTva8qZd{uob!oMv}$DpO^Di$I&g*6b?CC!1z{Wpa~mUi??-3Wp&-Hrk8kczzYi?iQCqMQxly*qi3UrDGh@h$-!+_UYAEvE>5auby*i><)qrI'
    '%+V;P8u3;LsCKhqYsI6(K)TBng@Yc2FPNL*$^Cf8hk+*#g@FzD_jWL7EyIJ6V4;v;5k!JT1qq&5NbsaF5-fH=g8v2ey2Mr'
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
    elif (step % 4 == 1 and step <= 713
          and not (step == 11 * 24 + 1
                   and obs["town"]["unlocked_shops"].count("YARN_STORE") >= 2
                   and "SE" not in farm["unlocked_quadrants"]
                   and int(prices.get("WOOL", 0)) >= 220
                   and quote <= 45)
          and (_fd_rival_n(mem, step - 1) > 0 or (step - 1) in st["sold"])):   # v12_11: no restock without a later fade step
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
