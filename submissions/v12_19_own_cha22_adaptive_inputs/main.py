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
_BASE_SHA256 = 'b28a173c9f23390d03f6964b04e501277a8af1d0eb8983bf744866ee4c3a1339'
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
    '6aelZixIR$TZ)!N4@KLzn}I-sKvBdc2tZgwv2`_{{hck>$|``A?CyzpJ##IhDl7LqdDh=qME<_pgqIRd0R67=*ErhzT^qAtA_^hQMwmv^%MJW%L!Q2F@Uzzq'
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
    'XF3_rDIw$)`U%XZn862g$BwcIJp4F;|4XnMqpALRh?;%)vBWUC=ws9M62vqjLIatSniwKfplolWZT1HR!+^iV7mo%=9q9`9mo^gqeLY#uXnwk=vNz8yBa$K{'
    'P#=58lTS=rC)>7w`fU(_5-+OxBDK0(fYKlG_Eq&buD*6%8tq=;4kDfeXBA|)hzbpl0*QDk29-9Uihc1g?GZUt&!Fabo;rubm}55t1oe6}>B-C}CTZBw`41&J'
    'h!`LqP|~c+4B1npKgiwI_>M=~L1&7F<WkPbyzz0md0=ZIKuk-iQcRU$wSWN~wCUt+(|z0Y5UB3Q5^YG|$lsW71K!l>S$ss!B0HOnWV5mJ%<6Ce*^{GgF7=Xi'
    '?8T7})v{DV@RZi4R+_B&LYr7|&B-#)t3?0hWz_2@RA9bvjs&^my4V}#pc{oJ#t}-kwp7H_?zZ^5+Qa9*XueC-cW8;Nt2DG%czI(cNL2PMdbh~IW|)J4bF8U+'
    'YSUSk-A%3h)XL?+Bei7cb<&+Hc(F3bO1q!z!Bm=8!gFj2xX5ZnNow3R$SY^dyyXqpwzib#XaX$8vyz0Yj?0Jko=V1|#!zw-kw&_9PF|k;g6_X?m+<DIr~muc'
    'vkUV`xr^_&U3YP9#RP%;m85TaJL%)Jf#7e*KN~NV@C<V1b=E^e;XGR6EyGuj3LIsX6(U(`(8<t^f$B1{3qvoBcQ`zJbMkitEKQ@&N@1^@HPtiYA8ME418F~@'
    '8(H14!Fw6VCGhI73tbWledkHA$><swW+iEAgp|^`L|L;iFeNE8{#zj{P=h^L>*tz5Wx4`N2qv2GYF3AXq*%VyBDmI~3Q9M<TePgWmlyJMjUa2J$lX^jgpHj-'
    'V<2`{;fXjq#_E1cAqXM4mKYtEt<W++fe(s%+*E2RV5osg7C^i3Byk7bC$*?ab(W}tQ7Hx&q?7jC>JCt8UQN{pJCIek19j{M9Hfe7X{(^9Ft`2^Iecxo!-=lL'
    'TT-VAHOqd_QgODkR?ohXyoPdLZ`%cOcelqvS$DXw*$3?i%hXl8np&Ylyq0?ejzR(n-U?xv)m(2FL1L}i!EU=~DYk7FDt#>T{!>xNfy!kM{FpFn8e@0j`QFfb'
    '8+H#m99glOvxlII6ZUUCY2OafEZi@T*)taLS0o0=VQ;aRRjnxllBFGsSOpmuer{SWE2H<(n(j<$2_0W1a!rcfFMG2=8;ISE-Szv!Ir#*^3Oz)_0s8s(QH?d>'
    '&?^Rvp7-G_j%~LlsQS(6$-8{el{~hhqx7@W^YgRwcZ}Hh6&RiDNfmk3h6t(PJ$Zdy=@D2;T%1O|6sG8T+bG+>eeImPyPc43B&0?zzOXwcxxo6HdkQRQZcfT@'
    '9g8v?Q14?O_0gG@qO;*FKw=*c`*b*!V08NkRh+i3U|`8}vAucMKBrzOkh%_e6?#~S1*g*HTooE6TKwTiyqgS1(K*z8cZJ%Tb0Eq&{`I%k)|S?nB;+eN?q`Sq'
    '^Qk_ku*i3(s8uA5?*nnGbB0f6T*<9cuy1(n;ZSZl8W3us%jo1f92LE0t>-X0{lrObpDIj8ekbrMCX0ysmC5y?pI<Epu<jtr^wGlQ*Vh*pSNlD`(Sf>wI<GTe'
    '-maDp#l4)2Oi-@%*=zwlAF<1(e#{ZO^bOq|US$SAUBBiR3`ftMF&&9*pvtYT%2r3BvLr5PyBXxnNp}R}^>AXG9B~RP>$|ksAhsKL^Wv;;Q0#N%EgFK}62#K)'
    'l`ksFOaSMVR9S{*vq@y2Y6Et}N3DoNZ0zVIo0&RCtyaT%N(QdZ@%B!*Q53oZ7;+$ezd3vHx6_xEmH7tuO;*src<ijo#LBVQEm$#)SPA|^|GCyt`PDc8pP{C&'
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
    '&{z3eji;~5OgtQEgR9CiN&^4uH!r&ipW45~9|dy#J6-dp>X)y7`nn2Luk=#pA%_Ei#koUab*T_6eC^KVj%?T`hk=jHmQ{F}{#La5_9IT82Vg?oGW7vPGBsMC'
    '0`GJh{FFbl-LUP?bTS3J934CZD$%ChsUbQn`v1wH{136ZJ~t_CUX_2Trz%~n<)B3s+bmJi^$OF~MaAO7@Bx%Y@CZ6NhSinP{w6eEDp3Xwn~T^M^=?jmWPw~*'
    'c*;6WGeuK)ECO6>$Ib1KC?SaBr4qG`ZHJC)<>Fpm8yHT{n7Hz4J^>-I^-dB;1&Tx3JKp25lO2+sjGv-eC}6ncmJx7EWlQ_!IlWCX71`-)=HFJk*~^L@I&G;Y'
    '0oInz<<yY-qe$qKd8n21ksb{)pYv?8<oyS5H=2&GbH^87@sHJ4ka?*0K1+Fcb(y5P1+MJPg`C{Rk^1x~-DM{wO9M-$9qudwj;Nx?L5xE3D@xZ=gy=5NH%Cou'
    '*cCTXqSWm@W1l5d08keLLa^={3c-QSJxb6rh)6;GlxnLJdlIWPU7d8Di7XaMLuNIU8{IFz8p7GaKHgf_6QCUS+4XP@nCl&@f{y~dWuri^<xuC~KzGAFb?Im8'
    'tz@I8>>ubLu4o%21*H7-^q0yE_*nwP8jd{IZhZOTt2+d1TKPOt%emBB(nBl%RtQ|lapxxcQV?P3y8?uz>K}uy6jqqCN#dy4EW7ja{v0w*_N8ZS7IpdgK=^dD'
    'z9UnR{RAHz`gc|O`HTI`dElMZhJOXBT*KZS7`y=ORK{`)zN7W66J4VUk13f`_{NGuN?2$GcCF%G+e)SI;_S_v(-#+Adn?-elH(UmcjS&G7ydYh`snfXPFlp('
    'x2vcz>ZUa-$klP94*F&)(0dMtt)<+$=YkfXjILWlMU4fyF`OgTkyJvy4i&EzCzB*QyeO?=Vnu43bdt7>n!H%h3BF>I&je%bi3P<2t#bq_-DF2R0ZKF($LVe!'
    'Ig{HCY8nInB3?)Y$xL|*(UI;QD^oi)d7#Wc%Q3Lyt+?K77wS+;+MEZ{?t~ji(`LIci<UmymwtCUDKWYFv9ME>P5^DN`|gcFj<*wXHhu9j*KLicYD_e(xV^G>'
    'wP7d4{E|DhVbDdRv(C2ne2%P)pWYM}&9t@i+B&z2GV5_@%we(mdg08Gl>otUGAPJ?P!{(Q=S9h!&GE4;oi8J;%3LWjQgQZ5w?g!OE%XQsm|vT9^8Jvn<Je8f'
    'sc)xmBZ&Fxe|t$RGr*xIu%(WQA=f=sN<|?s7p3kOrEy8DJD@F*hb8xj0x?*b+f4Vh(Mj~*I=h*2Y4tP~df<`|$M&~gH*by~m%LKZZ}Xn$9lsn2)UCD&8fAem'
    'cd$XV6wcN-%LcE}M5UMY@R#elFCG#z)u+9a{0_xOmY&5&fGU!iEEHL)ox(u_eXXbcJmzhP{`jtm<#)dCsmRHcbwfFkse8V?+ocP)d-9XxwN1}YUY`A~98VFD'
    'Xn-h8*^D4dq>$y-O^P$G6e-V`fw$CVIcX;Vg0B#WLzK`czjfjZzrS|Fj=St*rNmq$P6@DWz3C&{YLpUk>9f|?<s@!9wwt*2Qg;{U>)h1!TB)6dp2jfSwllRZ'
    'BZCT+v%pu^^d1lUhnu#1-*8JFFLVsgeQi%?9Ng`BFK}JSIv(H{jI-Zrqw6*tzq&Bt(fv)<TRcaV6Pco>%Y{mhaR|5P@I9gXP~2lrLQT8pJI(Ivx4-;)kqed3'
    'FKlma^VA8U&`*&{{eE`-Hy~4K%X#zS{OlK~M0sIUTgi5^8yi;)c(9dh$5y@?_>{)bRjEDb7;&l?<zes$x5-snUt>9EqzmR8)I}I~YW#RA2?dO>p^WR=?V-~-'
    'l)K$wB_0x$A=9|}xsKAF>+PpRrOPxQU=;<S*<p*4B;9l{Xf(8vyE*~!SBt=66T<I1hr~=Ls6|Qoy=m&#W8*5hX$E0I>Rc1<OYKuaeu)7FUuIDyg#XO#x9LW!'
    'Tn%T7n@T%SUBX5v_0F+K6~LT<#0Z7?3#A>N!H?m;2<sdEqN<UoCY5^xcgY5JX?dhHi{ucjN;1`vGpYa(#8ZZ6l2fO(X+kS7qrk=WreD_cz&OMd+IBAXzeI1@'
    '_g7Yvby*oQ%N*g!AV3*1=uk>sj!}O!AvkHF7@L-v*iF4aHs`%&E2+X*YuoX&*0z(Uq&V3P`B5xDl-?GIGkV@R>~X4wMaOeJCpOtjnBx0o`*~%8nHqHR`M3zz'
    'pkJ{0KPjvTv_A^3ET=nFhDdDj(?ed`Q|5Ia!-*bW>K)P1mhxbtM9D+)I}qV>wrW%tNYD~!(oQ;GkPs1HQ3hl4RY7KOo(V2SPTo#$)u!*n&SR0Qk5c-qt{(H@'
    '#K-bLk^?%m8D4b}mknJj-*PjT<`Xq2*Z-f-;G0lFgip!fA*HvMShjO$RyMt4t{pe{L1LamvD)BM947^@oACM}j=k+$;Ov~=e|b0RK)+Q6=4l&c7~Yc~fWez`'
    '9vt#Np3JSwi3!J-d`(bH%{$#_g^pX2Z+6;A__bKvr*Z73k*O|fO|&Z`zezXfB~UBRtSzS{aKED}Q0({#n#(@+Ms{S0K1qQi6KO9N>*Y}@wI~+7VS7sB^vV09'
    'h1sB{YFrFdr1O@hORL6Nap}Ra`hu?v3ro)1+_6EbCI5Q$nlGnL4LiaVk=ya>WrxmH)mzA`yfbN(i7Je@NvE#*U?Z>U>7Vu%H^f@W3Mq{dt@ip1mg-J#@Q@IG'
    'RN9^GwxkVuU^_2x<qC;_0?S})<0zU*ndNfYiR&$Em*=1fH5{Y5zh^1en#X&y)dh*ypbZmgm+RD<yK${$l9Ay-Y@=eYN6bP*me3@6Kby?w>IddDjIL)H+_tb*'
    'Nu)A-5nAL;g4iJgjkiZkJVWv&k?`{Li;$<-^oFx6i4ruTUuCXQM(}P_aC=$rF1>`U(MYVNNvd(e!PCSzz)S4~c?E~Sa_FKUF_7SH3=gnxlQ7_Ud!&HB^r+vw'
    '53EK)(~yiO_ed@i8Z8Z$2AOC{g}ND#R6ji=IUluv!p)*YpU8%fZ4_MS#8dI{PoZBm+tcX5_cQ(UV7yHIU^A}c7|8>0K(*FZNrOn?(lsbvuqC|X@q?23nMGGe'
    'o|$w^uS?UP(tm4M#WM+a3^3>fx(J`(8m0K3TD3|OlF%fu8p*rf<0Q~ywIj4Im+nZtd-58@%!^muUryhiyt(-MGjm9vA%mvcj}!fknx0w{`jMyt1zf!IKimWV'
    '^ZC=m7v5~ODo%i{up+u4m?E+4#at<&Dymo@eVQ7tpA<^Z17h`6t($e;uGUF^TE{(>09%az*>-~F>Da0oF5COA7Y`lC<Fw_+?<0gJDj-t)99qb68hE(vtFv0y'
    '-%y9lFX)*0(XxL)M~|v?tcgCMKcF=I+me5wOq&Ra{!Cxxb{EwB4Dyjy3|P?_jW5m>N6d<<-h4n$c01-Xda&0CX%ZwsbfFjBBcm^iQN#k;hJc+tXJ0SPE-Dp-'
    'LNv*V$+E^PMHKcN{x1=0Mf&+mqHL`shH{eW)Nwr%Hz*a|!D*;%PmUsYU{^7@hI?zFh<(gFS39R}!h2cPk!^33d3M;(B@NS7!@?@854F}&f9?%lUvBQKD;u?a'
    '6_uE><B)WV(l+t#Vn7UEZb3`&aY|L>jh-URVAY3fOd-Xp6<J*izb8X;ZsLrCi0+PU7`s6RVo+u&4A0IQMmK@~E_X&eTpbwGza!sm@xTpS#n>m1XD7XZcP@;z'
    'E@07;p?f}qhabp-#8oOd;Y!|k<Z!C_42a5ykMSk3y>4&t->`RqE+OC5Y{UiH0U53G__Uk(&^dI6Dt76j4Z+2%w10(Kh7U*nfQz>o&4K68;D25J5b#FV?(go@'
    '1?GWc<GE5~E`p0HArT2OR|&B{sr>~4bFQX~U!%1BF2#S{H@4Oj3Q)J)5-Uk;F(YLUj|f=<E!9OFsM<`P2RvzRMMtL>qEb91SVig-ZF{s>vz1iyVW^jD(fmLR'
    'p#Q%>%2YYVdBTxG&vRisQrd~DH$VnSE7{UO2F(^J8jjM|{!@Vq4!<r~{V@UkE5i9{P<}$@;IJrKdY)c(f5UO*Tu#x<mK3<7;=7I#nop#v=&tvGvyUNJi1`Lx'
    'r<CuK#+tG}A5tcGOme|C_q*jB@$v6^I*s(E?NG^!)k>QC8iZw<GX`^%R}e3Q*fOKAkRit<(GpXSy~ux@hk*?sLxiI^f(=jZDGx9d6(pF%gz(x97j`Gw4u&^E'
    'QsVd0cXd-+c2a{0n+^UKe^C@!KxO`i*_*kICYueub9x!_@ClDl8RUx0ifX%(MFMVMZD1q{gJE-rl%J*hA#KQC{Rs#-jYGJVBpYm*46}Y5!J%>;oUcgCT(H1a'
    'V&;~Yt34l9BM~<ydBm@r3ZlPI#v(a698R+t{h|P7Q12ulGpOETNXY51f4iJ&RTdvXEZJYq=y>wpsZa|9f{czK&-I8C)#}yq0fSE$NHA%&6mX=U<h+<i@{kt_'
    'W~-e;=r2rY?Wh6Uen(6SX@AAyfX`>35qELIZPil0a*-Qh1>{ypUEr0@p<EWcH2$9IlOL3Hs*gKH!R{C!B&+gL(_5~bXN0qwDaelQj9P)uPNvJL4BH(_T~AAF'
    'F3EW!$22jAG%-iCJKNpw{`Uli-lfvECP1mb8N<}<N$P>?8%f``i!l={OoR}LstwyD*^m#L7IItwpn0slQ_3VTn~fnGCw*GX0%^Zw`$L(s8jW;CtBPuNNvnom'
    '>)F*|MTe`uW_6qQxe!g2k*G{sJk*?+_Ss`s(86PsIHT-z5cP&3ZH(V2&0gowXWzcoQR{01btEjucge}e=ByQ;lMBtUB7giQ0+}4X_~5kOQY+n4V3VdubOOo;'
    '{oGP2=x4bds{s*R(chOrbp^f%sb7S|fj}2+6;nyud4-a$%lqjbq5NY$8xDGxvvj0>Jk%NGJrAyxo_XIYk^G;ZJ3gex4f?sqwzFZu{xtBf-UR0S{6gS3rS6Rd'
    '#LseW^!r5jrBf>B+DKh^jB8`w$Ixr_F`kCPxiaiBX9)!U!Z32o@XHiwPov&)F}Z`~>7&U4jh@Qo@OPN$S7*Nl5SpErmXo2S%STV8ta}fvB=li!$HYI@S}m|H'
    'e{F4lm$tUnl*Ru-c32P(mLukWCG)5TJAW>dA>!p^kd4|nallyNq|Gq}3!<fO7RcUOMIel4{4}8scZ!N0OEHbX+qb9Z-M8;9D>#GWOeOfJmN-Qwu9YHwY{)x$'
    'WEF<HcNEkjMN8POlEiqbR`M*m#X*wfi(>;>iz~WBK+jIfKd4!JU>&C`jtxsc-wH7!=NTz4ie*w$9-EM`EE}klB)3piE<nU{Qqz$U?UHE2knj;6nZ_yADZ|jb'
    '9Z*xdtBg0&16_t)UIbWcds9dpN*{<WDv*F&6Lr>(u#40U9O1yYZz5RH;5fG$HpJj+D&P?wP<0btw<3XR42vQm9rTG6gRW(q4+4-orVA^)5XONDb;i1uI?RP('
    '`l+p>^zk9>f~nz0X(&?i(+t&41Z|*g;n7XcMsP(p?#b0?_?}si!)OAuWTvQ&%J8_URbhhxIhUYICv3yX0F$bcoJ|=XRhqP`2SvJZ^6HYjV0!Z~Cxm^LtMj2Y'
    'l6bB<HTodow%<{Jo1tCGFUO9_iCqt~dRgk9DGKq{F8Z)|AY%zHh1n(f*jANMcJUB!naDm-y2SS>imO$ix*lT4N;Lon0wwtj!m4K5;j^tC!p5~^ck3x^SLkR+'
    'MZf?iN6kiClrN#c9{9Esdp6Jfpn1;fDU?2>^CodW_&a#zqL-OmuM)?jLwKCtI!D9Om+R-pb^uDLc{^`JM?s8~O?Es=z#+NTO!k@wKG%4?#KcT%IwE`OzmDUJ'
    '?A%J1TyN=>XBY9Vys+2O3blv<Vxj4<wLpamoFF>32b~ktJV|5bT-c*=cn;4#qM=%C6_bxawFW)5x=xgibygpk;3Ue^bzxuC)9*9{&{K%N)QY_gS893$95H-N'
    '$DNWRFfA687p9WJ>dqr}?g!2f2*P`!^GbPoJ=6-#GSX(IE%B~K^G2hN)}?YzfDV^eooDYjRjvBzlfIf1Y8aUSHH0y-vwDau;%RVcT)^Yu+t5=@6~jbSO{7Oh'
    'eWLkfBDwNIV-i@7VWB3Yj~w1D8c*tjQ9d#o@tr_)wO7_IDlC<I)q*?yO1v5!78nrbR%#$tg)wT8jT3+d#;An&f{~_;B)Bxr^U%z@AG(>={x8s*s8uPDlD#<W'
    'qDalvo83`l<km(aqP)_U1XjAFj$X#!T7|lq;=sy4Q>zsp<XR2Xe72ZOMnDMfC_B|Oo82urb`qHBIcg)ey7og-U~F~YocwTh?j*e#^{yr}Tgk`|7(1NugVNsP'
    'r}Js=-qIoRLp#L{KLL@gwd?%abAIhRd4r)_{0bSN_v1S`>Pl^9q>pbNQYmJ1B^b1Jlh$6+Vr#l+Uydn5OEu>O;PQi5Mn__QYVL<(u>TUh<b?N<Q8nsG(sz<A'
    '>L5d9j;JL|65S6MH&Awd2d5YwFUQ7nCR${@JI5s;O<Q{gUrtw+?+t?lP__uGO$HCvV)l?V%TJ3swa{FL`B1s9($46hIqqOiU*V=&3B_9lW39Nh%V9p+O1~+J'
    'w=xCXh^y5xl6ayF_N|oxW8JI}MT$3T`i)Rx*I(njWR4dk5aw|)UUpf0mn=m-Aj{0G6WhgYdBXAVIJJA&=Gjr-$tRM{4g{hp&MZx2Qr)Hh?$LkuacYw)EDioT'
    'z-VrGwoA`;=+`d&cMqS%p)(-EL_D4V8V>@UCA!3JK?$XjyqQoC(IpCv=*ok9ZELIU<jEm@ohE-20_{`qDv#KOb3u}wi*KPg8gx9vdj2(>R(To|(}2&@I_T!~'
    'Jz=6l74WYPJ>eHk^CB04qUvGnO#G&Y6<z5ndiePje#k>ku2df>c!DZ!wmWfQy|gzm3<gWqn;jd6S3M#yUfW}w_hjtn6okoBTT3@k4U@!}qChAD1dZfy_gL4G'
    'yN8i7P~GuSsu#R1yFmL0no<c)mHcU~ke8H*KhM)~#0)lH(ey}JHwusSrO^L*YKkX9ePn-_?WzCL{`o{Jth+e1#?KHbn!E5*@I8)wcRlp&Z;YdU7+1u@6ft-r'
    'KI7BQJ+Y8QjQHS=XQk+1eevS#=O13bJ$)Hq9NkLuOk+tcxn73>JOVY41tY+J`sLO&yB%z`qd~^;`6%A@BfOI$+D779B|2hM@hj6C>Kn3g&L?YA@qw#CGS^H>'
    '@y)rHf?)suG!Di~UaEPLf&g;o?FzOg7)-ui0**g~q3ISdG_+4@%|D!_v4U#W;BDl5`T|R>m2f$od$r`;$q9L)huFI5TnwvX<{FK}3F!;F<mT_3f+|CX_<_!D'
    '-UxN6&=sVi<yJYb@(;3k*-G~Hd|CsXZx{;5XN2ZUpz@3K^QVXQLdW?s4x0?a*2C(M)-*LU^o6c4xQp0!W@e6YMN~b0u3?Nn7DvE*{5y9`lS7Qo(fmkGJNe;g'
    'OKCBSj#8~v8y-vQ(*RPo-aj?vnI^tz#|Jy@K<oj-dVi}hc4@Qzp>F#(+H6}|{ZOmYOFh>r3RdBOx8j;fnnwIuJ|$XQ8+w)VcB5o1&x&I6$+%TA7{;nKzJvUG'
    'tib{3dvdGf*m>Dc`E{hu9ARYg`N_rWvu8N+8vZ<a`7)1&ZVpe4{)0)lLTg3mPEo7R9G}vr?Puba+8+`XTh%7Opf9mHrnU5gbxsjBZ@#e4YAvOI@+PW+VYmH>'
    'O2>g<`{V)GT=s*6p0>?lL^?_FHol&pg8b8})w8<gc56LO?B{jksG8J~^2N?g;&AW`Be2@DSEI45QI>S;(vW>oeQbX;=*)7TtgdaHi=}(M*Kl#v;CH~e37$#<'
    'L4r;Euz0YqAMxx?CfC<Mr;MHsBMZb+V|93e?Y@C3<j1*i;1}^x2<l)m6@#>F@07}3wzoQm`jIi%s7HQq$W*(9(6D&7rbSqqx)whj;B-~IL(covG?r_ohHQ;$'
    'N_aOkuLWqj<Bu<Hi^?CLSFP4$a8dbjq>cjRdnNL!{Gg1Jl~vnn2mF=pR>I4nW$E$302+7qNxuBfMrh(J)~w#t*Nl3lY!zJ5artUEPMP||VYncjG4Ul0ree%_'
    'UN#%~)|-vBT6n+g&GII=b-rQKl?kbphU?9SL!{Jmhmf!fCLQ{=j*lonD+ufQl~1^)T~9~`QIH41sx;tYp6CDy@@kz;(5l)dsG2Xq$y366(X^+Hq<nUBe%(%S'
    '%WmUt9m^);yl|Y&ODfhjp7I^3O^|sva6`?NCBwpQ(4m)JsGcU$$z(K0<wK{;vNy6rjmlEXJ9&P*6I+M+<FyW<4W{nUTkgzSmAFyj;sc_Nj8ji8Oy|<YDwC8U'
    ')@dSrOCfGZ@ySAKk$<p^|FKbg;2sxP-l9O*d}L)f2L@^~u{th~ly%-Udc;a7%LOt)2o}N~p`0D`sf+IP1uE7Ug_7`t4s$U4M871wLip6zPiJ!wEMUV<a^dZ>'
    'u4b#@HXu)l31WXzdOy^DSQEgv+D={+F!c&s9&00?dBy6qt`72*LNGf=(!YR<*SdRFYN$hPc{us}&5lf(jzA|LFZ}x`^@UP90GyM4=RAkieJ<(q)U95S8O(`J'
    '^rh4sv!`mYxeL`!fxlYugxPUx=H3hJC4IO}QbCvYVb@@y<Jhq1u2TK+YIVNcjNJeoUF5=ZuVjs8U+98SG=9tX!d!p6GXuperwgre*W-M=pN_ukwLg|i9Ls?I'
    '|BNvPSOQ}e(Bm!u^3M50<#qYG_H}iMdk0;LfSFhn7&AgFZU}WG5W0fGK~dH=``8_&TiO{Nfmzm6J{H|ahgXyFa&G5eV&H?FWH;GM_H)qGo*C970_#DcJRSl?'
    'Cu<J_kuWYx01^6-z)#XOa8bMpaZ=dKO2v)_L>Bjt(m}0Rr{<2*CS!CC%#`3wits91o_&$3Q;S9_A9<}5TWPVz%Yw=*2DFsvN%VJ@>QSf0V}Z4*EA-08LS$OC'
    'x`>z!gNXUfEfLJ5lj~BthOW`ERBX8?n`VF^5RcQ=Gmt<n0K%Hp5YQ8h{aDjb*J|#zL-6__<VP87)XCkjA7TDLFU+HkE{W()hy)Scf&UV{;2#*3!6`c0(Yr;4'
    '4##h@EP92isA%KOWHyL?p4?5Ma~jutBZ=O@SJ~ZFHfy$``M5U)wt{2r_IJ9N=rc-%NXV1(3-<{VMtG*<@ZceHq41DZR`7(0pFB}C4xZ!ah?Yf9j>DtCyM_+D'
    'bDYDP1&}xeJoox2dJI)wf~lkS;3I%_u+F%M8fy?hV>oqfrpdFAf%Mx3+zH-p!8M~I>r;zBSq56}Nm00)fsM)8TDi=3PUcxVC7-qg28cV|Ctdt+x3_SUCgcpL'
    '`9PpGE*O<Q)`TzpbawXcloI{@u5)+?69is6a9bv&tYlucE-~n1)?d;#L;u17iOAojjc~1x6TD4;#ZkCI&SS`<YFAEw`boytuKfJ^&END8CBfmBOTI;AUTnKJ'
    'GYW9*_c<vl{U)8b%&voDi-?~@cB|JQR8cUY2B3{=JMpvTW^3m-bzbVQg7C!P5<&C3UD9`I(v#Z<fv^2cTk6#4J#RQEW+yex!~E)~SHB%jJ-kD99HP&kobUF@'
    '>9zu1{6vr?<b!GQ8W5-7f|ye5RO&@i9g=E+leS=E%3ZJ5zsUq7bDk}r-#r*YwIWnly3bk;6a0X+s1r&xwC%v0AA0@U`ySklvy9<}`WTumHAUBmx?X1qtZsuE'
    'k?SwAAq397>0}e4;4_%}XM3&U5VXDKK5&l6Jo>l=kII6P3pry=!xI2|o{}NsX$pPaRWW6+LabT`tZF43Qk=_whRX!gm-39&xC8om4Sgx4gSMp+H_#=|y$X?1'
    '0qFw-@-Qjh$$5$K<?wEJB3PX-L%E7Su752ZU-)Xnip<rvN(qQ%^7^g<x$4o1H!eiVw|E`po5at31D&I@eo6_f)N0a9oQLbRXW!uNQM`ehU)av`=_pmLMzyJk'
    'fXhm8dklTcgWi6A_DrD9a+@M~_N;2Z^ST^=Db@^Q?cSp2<_piR53(BP^G!6j6Z;Tda$cZ=gky5!PEA)Fd(wiMH(O>{>z*nU9d=70JDB361(K$&2q_UikB?K6'
    'a50az_?=j(4QZ3l!kA#|LjQ638@Q;fg;;41oud(_obbwhS4eCF0C%?donn{j*iJpiUDzr<3fhG7Pr*r8mB!K;Jhjr%F2N3$Cg~<Ed+T9A32j%U>K+vs8Lbf+'
    'sm1C?>RG=MEi7+p)uQ|#0T`w$Uk55oFN4y~8m2mJB;MLNPn4BbDO9{nkSoBl$^$r^>|A)z!%>{y{drNG&K|V7uJt)4($mtugu^@CPtPyBPi<0MroMOKlG3!b'
    '^^KxU3&gF0g(jnb*+xVbi;6mif!x+Jh5>z0pKch?wXdx++-oaDW%kv_5J{XekbrSdqL~YM7KNlW7|#3955#quJ+L;h&#0)-_%7{<?u(NbuTFjCoG&H|67CbO'
    'Sq^;Mw~Y=83=3BPlV;r`rsZffxz`9_?|XMT$DrgK{btI$$=w7N`ks)?n};lZvT!ADjxkO%gzsTXrK+&G!z`n<H@WSAPkMSuzWJR)M)N}?_?7X9xEgaiX`|u*'
    'Zy4}aWwhU3Q>0W9qznb~5n)Xo->Fw?5uYF-<{d`Y(g>DBVE8E*`J0k7N0`0ASMwZBrb<ha%Xp)`3d<4#`e7cEsU4;&ilVBY`L8G=phRzk@*<6l7PJWAg<-@e'
    'a}!Qi&|%tZ(z)8#nc6L{Nf6aYH%r~Hn>cQ)(T{o&j=mt@19RSN)6OUV4$M|q){~d#XTMYe6Jj@M$1If2^P7_wr(ZeEGRw}0A35=H{tOu(+*OGp)n=v-h<hgo'
    '+tQ?w>%``m;2MfPtWHZqae~oLUg$7WLiMoW_-;Am^b&f~NlhX;+8pks%TYseX9XxSRq+T@-9a0bwNM-C95S)8&7;Y9^nj~9X0#sc2qMo6vi@+6Tw=e6A$Qk;'
    'fO*H)?tb@|S10dIZA;pI_tn|?>wlcRbsw_ZarfoP-^rY&)bJ5p3a~Abh&Az1bw7z(_)~Q8QFS+owm2uYzR(NQ?va%-Q-FtHUm_1Sf+qc5gw^}>9pWe}!-Yz_'
    '!B+Ixy?3EnWLj!bQ<;?zkS?3Ub6w;(l}b5pt$JMNr*ZUGtCOk1CK7E1)Whe?v!lpsgvrf#8Y)TTxCdKnqa3(Y=klqVpqU2pF|Sn;2;g0M<6B^`VBN=)ab1A+'
    'a2pILP+qC9VgIC26Tf|drX6B;KW2J^p+o^kWIntaWzh>@Fr!SMqp(8{sDCCVIU8)cJ(n%yD7P=jsx;?TVTS?*g&v;#cyW5JXPYuWs=jiT3!Z${3%kN;?*W(w'
    's!AhdIO9w(F;4%6(_>8fePB#%o(?8&(*~FW9uxTfNY>j!h?AE`W@og0tR*P|o3Co`6ZImFo<BExrG^UcXZm-zwd1IDkjs!qYvy`St9?+T*L>E9a6rjb^rW@h'
    '#%d7TOG76z)E5~E?k9K?0R;o;8rIKb;GPZd5VH&B{%ZL^)Z`#!gg@|1?(*c_DJDerIQ;`hFY`om&-!WT4uj?%{yuE;@i}X2DAqCw8tg9a(O=Y*UM+$4;{JO;'
    'IfIec=6#T?mm@d@toEm)j=F-)RbYXRo^tyj{>FBjuQS9HB>^wO1T0`^X%?RV6u5rkY8TnHRfZ3@b|>we7R)bLn}oRq{>VWN&X-bHK<5f?4|4#K(9CWcnk>&@'
    '34vJw3OB#WvT4LAeGs)_Q-Fk2RkI8@1k@KHRV743PbP<hoFMc0et0z;p?@i^sK&4Z((-<?>ALtWCii2saxBLT>5I<5Xk8XYtn&Ah^S9l17iYlR#csAwHFLWJ'
    'nDLnsNEd8&waIm&>EpE7`r^S>$ecQ)1gO?{IKNpJT|4K<qx1*pAQ#Lz#K5=#oxGd{r$!6Cvb7F+B}=5TqmCOsv|$_u_SV^LdLztDbC)rM0#o$GtcUl+^WN-g'
    '2!F#3KSy8WF|s_%vA6(unBL*@uvTyWZ-MXrh9KBahp$$f&Bd_xEGZt4weL8i&jg$Ob2qA(C`j3lAVZUnu7!A*Oxy`jiyJ_~=HPMK9^V!1;ea9};9Son^N^Vk'
    'bWzI(E6O11I2|^1#ox75ed+X4Jv>rX<;~AL8&)dcV&hKEVDDIZ5YMaC(fz=4_>XKh0cIha&gHUa4wYr!`ADN(Tkr?C8dijyJE~B3a|h01w}78f^bhZXF7j)+'
    '0KQe_wRuT;_pOmP4|e_#yiMO`bKon^i>4;Uofe*j+^aRAHUBTM%xFW1e{nv+1X8%CEc?fSYySwAbBrGc#m0|=uQz@iJl6QJ)ue<X3sk4D8$-05BbRi|*z_t}'
    'oWKyHgBHrF%Q1s$VTs=S21M8a32p?|sbpy*haslxa)w|6BslHmQjNePD+Zr_zd3p5M&uu8hj_BXS8>xME@8I<@bPVY2%I3M+CF5+Sv#)<Y19&}^IPYtSRHXc'
    'wnFX4*3B?34zBk?witXmDG0Mi{KT^O`1%JP=_QS>V<-N7S~R}fpTbc4@?O<G&^maX((#=L;DhfI>bkSu1L!qgI#q%B5pH8Ve18)HU7$bX!x18;sI^9>6^nZw'
    'U!_Ro?E*9pADTQMOntDC6<}f(z1xf#f%V`D)`vpCn!~xLkMUJ|q>~GzBQHTi?L*ys?W_ZqbXMSMIS}+$@2IWDR$^Eq4nHXh649A5FgXv1ev52Oc<BVArcrqi'
    '?HBg$6s{j2MdTYAUEE}-c~ki{;G>4B3}iXRT#4QzBpbPKLB(7WM903RB8-+(tejGDpiBuHk<opWZc#k+KTq5Fkeq25EY7r3Z$YOlytQy5jxPZe5T5G1#~3{i'
    '(w|hBAo6sEEfS1gW5RZ59b#S{2MEEKeUL7I6!21gyshUrpB)2aL7y*0H+Sw;vvX*l3x3$@1R#KPyNWtV(;uGM-s*uI<N8A(WcoX;;ooXB#La#i{}R3aPNVT<'
    'b*1mn6lYZ_KwM1=iK_*FtB|-ItpDQt<o6#=&(Hsk<>0~3r*F>QR@(b+dn&&nRDF~>07qibR~IlvD8WtLN5c%IkAWK)?kp5@t@AoxqNuiZ9<K6e`EX>=_BLx2'
    'j&=`rLd^U6ZUZaxg0SMGEIA05$i?P-U1kt<BGG*UT~b$cu(h&-t&RmoBifcgE)PfBGM#0}gQX3}C(^0`M1*ETTUE4<gD6db9Gm3QMHu~uU9)wRN!)`8Rg+OZ'
    'r*5f2w*}D_isiFEZ$BRWW?rg`b=fU$u1Z6R+iGIvsoFGg%_-(4ndMKM$u4X=5785Uozl%p&mkCg9CuT8J&UlhrzIFB4Dx{suygp$R9<qr!@90N7+UlXRceKD'
    'vMHY<wu^gstI4yw-jsnh6F28DNCwD{rk4BOWAH^aKb!M<5{VWQthl^xF<Y_Pks;?;@Kw$WR=T)H1=B#?ylDtHTQ#J^usBDM?L<<Zy~*wdb^-rL<czxqAK!!z'
    'FUJ_OD4OV>B*%2qys+viJk@FSYNK?XrZ(Wl=cy|Qc@4V~k+Eqw6?)p$<Fsg0rC#B{d%zT9=!vH^JXBd6tteIGN5sv(+K06m4y<?rE!$XP-x^b9>an&rO;})_'
    'il>KK?_Fn@?YfE`V9AIk=7VUDKk#X>7FDBGvi=J`{cw~z3uOyfp2$eA^RSn)0z3wqg#<gM#F$r;5#Bh)aK*L{Vg$*uzv&uD)G;3*qfFf-g{_u~q_ZFZiEanR'
    'bqKqh0|g@V*rj=*zpmjPkM4R8(G`Y7E!bsau<7YfjERd$Fz=9<Lh!sOydiA}dM}CqrE&KRlzHjKpCA>$VH!Ln?4I8H%*xeN5AFSYM6&wQhYsaX4s4SbmefU!'
    '!1qutB$2__{&-uR!~7$KsE83AsxMY6gy)iU3&x%A4HTmo8T`x}JIEJ-8EFT)1btCnNI3J|Z#3)3FRR(M8O%8c7EmqKVc3A98zu5ql>1DAS5pT)gvKR_)rLMw'
    'vcGS2Z*cp%o3>MG<_slXlQUvr^c1c?8^!#Wm_Su#EFgI6eq&-v^}__~gu0oi>T;PXL(C$Ych+DPOE-ygovQ5_+9XGGE0uGvVSva`r*v?-%OvY=eIquRHVE+z'
    'D=L&yk{c}#K3V*Qwq5Z?2~AzS^uCXs1lvcg{rwev&3ZGO>$Q8z<-b)wLoF~!WWGnivUp2&#iqe1hL7({arJO%nxU45`l-$4kgPEAsF&Adl0dGg=bIZg_nv0h'
    'Tp1d7SQ=XAvJLc&<*dfGArl*?A1V1WZ#doajBcTQmBK9?+(PDsUVQV&IV}ETudGJ|@-Mvd4*fNc1E8cym~L79$y<4I)3!!@-hWDh#e@|FuYk*aF_|xZhTRI!'
    'oxF>VGIZ^9ivj9p8GH8}W3OAlwes#2TY2}s-paeTwv`v{y!CJQKdkQKLG<G6*Ynq>=a>|S<So1e?}p1e_N`N{wRgh-3l!uInt_NiB%gh9=Rzl31lqzH&nL_G'
    'Hz1d6H~xx9U04L6n<{fS;IrQSRfbprEYjQ!N4KQ?29XFW97ie`KOzMSRwuy&)C4+5&kyNWHU@eR4}mJrDRck@n+bOawqNv&nC55nfCbS6YnxA$m+SCqgkl)='
    '5YEDMG8*<DXkbzweu;c$bT^q1T7QHZeDp1ZR(tnY+YPa2=zYAn&!C$WW!7RfuKpZ-zG3jv3G4xifgdxhljT25DT38eU%4^(fDBhrkH-xJXb3B_xWRad2nFF0'
    '%*-UZ?~&gmdMKg^ZMm4#aZ1!${D>BO>eX)tU0LVukLPDUcVEGe1hH9QX=K(3E#d)tr8dC($z(9cc2E=W7nwPozCdY2BeMUo$2+R{h@?d5niEy=zii;Ro@H5E'
    'tuNLFXM!^>EzGL*c)DU3*XS13VItEA6|gJmpe`yQiOs;}r-fBhE_)d2Vxu88JwYeuj3Vi<2>b3!=)O2TedBXw&Gzey)1T3$yt-kGNE=DCf#^{9FTz66Z?q_F'
    '#Ll;Rr7#|%_5c1qUF+S+ix;QwsA3Fu0lJHrlKe0H-jUy=X|z9k{qhY4)|l9!&l|XA*n_t~gI?hu@6LYZKThF3p+27SzZg2U@x`rCdC*&JXxDnO<M(0v!QMr$'
    'C5lFm)B|-t>Ic@frp;g<54!3#?g`Wv`k}U;lIQ^%gEzvwz=H)o;bIOUu3ld9s5+hKnF@nhe2VJPr#Pxb@Rr7Ezr~k}Po8y?it;=;H9bJ#2dRnY(|(O_IX6RS'
    'd>FP|#q*fZ-c3kRs?81w@ka@gKsE4<jg8-7PU`TQPQ3s*k!l_;_`xW%k2m>E)0L0H>;j0_oZf)+dA;B>ya_dG`9iyyVrM!wY_UAT^j?aO^LAJ}rx!EWy#aS>'
    'j60!`Q2>gKs!ppoMGzwLvyP5PRwgJwH>(5wk57E6;sZ8Vf4{-D1>WYc8nuYBTuB+aXEv1iA%|!NwQ+hEo&@LvIWurKI6;aaKTG`~Y(59_d96tcP8@G%jNTfK'
    't9eq8M3xG_*N#;FO4xH8Sc}_IWwDfpO>MTv!-er|W#`Q~N%R5jbD|0zjdX=CVhl;b^{msb<tgHk1a`iUR%2Vaqf`U-ZQ$<>wMZgJSg-lXM#mMAF;s4^sc|o('
    'zecTXSicaJ&F@-UJAijw%5^+{9$9vDamU$!0<e+3qv$<HIetm6Ivm&MzMwQX^h#}HNj(Tl5i+?4GewYXgFl<7+=bjFA_yBAeKBPEE*~_}k2Lt<rC7(M5gqFY'
    'hYr4=6(LLFM#uFN&=wy&sg}7-9ajWRtEo4+42N=Hbq;J}A5@KsnE;yIu-<NXUIo}V(*a|P3=$0P4JXF4OxDhKE)nrts-<{J6#01;Ro&2iI3re6vqme*i1^^9'
    'dxkr<7AeajZ5i5$diyA=z!^r{S|oqojs&`+t|6nCvu2+YQZ6FfMM*C$PQ5?N?o~J@{7K=MwMe0~3Plc$-KXxV{|ON-O}h=TSHm@Yn>h*+`T<Wo$W(njdTM2j'
    'F3`qayGW_ZnTsff-WEZ+ZoLoOGAtEAFK^pKdp^b@B1a#^qmUc2Q|(bE*Bn!*Vrig;<H%0_M@VI<Bs;@d#?IyRC|ZUOL)dXYJ%S)HnZV4c#1~X`!1pnX7Qq}w'
    '`b54ZkQriW@R8Q;ggrg7fUq1whuT~zaI2Jv6@Fv;K4MaiTfN+H_*5XtaBQ2N-9gd+I<<W%Ep!5A0=RTk1}aS;{aG%AQI)aj55<HKWGzx4E^-6sw*j7z0JFjT'
    'LSVX!X7sXCKApu&rA?>Nn88IcTCdpQR#O4?szU;(o*0X4)Id&V96+B{J(mY|_B%yM3=pjcF<W{KN|1|4G*0x57|`|YmFOpOQ<?q{+H91En<b|v8K%__kx<n|'
    'HHm}J?i*Z8QDAGAu#=^_7NuB+F37&Q5Cf|;pUmK*sG6yl1#>ve+mG$2F413ov8&#Gq!Bh^3?hdg%}xMb)B8p(DX@%DYi$ys&FE>ww!ldUl+OSQ;yKws1LFog'
    ';$Sg6rCU;@Nky<TFig+*ry=;HP1^<-z)6u}m#vO)r`8j1=ekS1$pKBed|X&?h(6B?6e$bJYO|u?C&J_!+{N}9^<MI9C2C*z=&)rJl;k3&pkqIn$81D`p};>2'
    'G^MUi!H?m85`>^&gL;C6Hdq)5BFVpVgpWBMORIYY3EX_-Ka`4)ZR5He8Nsbjam+-8sWcq6=9e5|9D#eZSFMavTR%w?qa+pXv)q8n$BirrPR~OYrf9W^Nmkzz'
    '3QY}`aJV|wt7L2Pz;d^{NAd%TdT*4D#y*E<u|bbF{z#oYIjS?%9kF_|$pX1ySe)JfmD&UqWR&MzBD$JPZV{nmE+k*+i7$lpk1*s7YMjgWld)0ple0n8f9Q`;'
    'D=ifg0CEH}KMD|o-f;Aguwops!565{#dz*k9rcoPQP1D^rcMkh%PMFe5abCwe6SRoQFKBU0IWO{;4B&O1EP-4qiuHJQoY$qXk6bn8>mOeIPz@Zw2RddBoWO4'
    'CIzu)hc)gnzTRw3+&WD%=P!;vQAzFt7v#lYFqdhDt8guL4dw-u&L981&BRy`T|J=rfEDOi;|=_g(ZY}#`gdvob?GDM_q9I&bhVq}>I_GjQJddPa56@u7YD8b'
    '>oMIYYqElI-~s$G3U7P1(x|oBupj^U`uyDmLL{Lq>AXRsrMy59x2WT3wC#NM!`a!-y0Pue9TI>kVv+1QL~B^xkMI=AwGQ4~p?zv$pOyEs$^AHAw{95w+qFjM'
    's<&zHba8Q*gvxIMVD%mrDY)tFleA!ArPO+ypD0RldXqm}QSvo>Zcs&F>EtMx$wurzKH;iNDb|&#=3tm<BNWOwxFwKkZ70#ya$y~NqLAoD>5;c>r+W30jEF)&'
    'p;Uc~2^pUIkHh&;??CI~3hB=B>P?Gr@1leU6W4V$Xj;kLb#!JPCT4e-M5WLYSbH2|;rpoNyxjQx<l^*vqq8>C-o<^)dOfWAvODbLxoqS$c-2_J)SW7wDu~@%'
    '>$gQ56%SvkyX;PZ&8L4FoqWnP3-Z6aNFql3M{3@cy@biqVEdsY!IWS_Yj9K%D>)jl&h>+sic8;frRfqAZka`(<ERlFp{xo_7_Rols}n@zx!4H6a)u<`9Cv8b'
    'G2o4uI01?5FEbWcbERYk+>#=R3m-*iq>I=WLamg`_XgfkvYH!2)Md1_2py#;U1a{HcJ0*FINDq#eG{2aeW6k<5Lfk_QT3BtDb?P=f!0I9MT|#~>jn8Rbm2I7'
    'CQ-hOTpX052Wle?V!^eh2^N*a4HCLCk9ZFq*-hzdQ)7zq+#eM+<q)YCLi<n+OlcE=R{~~?yb6%iWxf7Qo8o8n6{=Z~@gy2eV3W=0;+$KMA;6m~r_O}9cX-|E'
    'sFnDL+?>!TP05N@Q9roQFs2gzg!-C0b`<LeGW(*YnR>ztF4aF@YZt(t+=)HMa;y~&rdAw;MCw4~9%<$*$38NoQ&XMd1Om9_T0X@U;avFwhbv96pFTY;(0f(C'
    'c9TIboy;!UUJJznM~6<0Jt~Vyn&+qmK2+qwImdOP7tMS~o{k>mNyor2ni=`po|XTcJ2rH$2F9Sa4B3$FX)CxZNRy?99w=bfQFo-^{H`IvpV=k47an`35Cfc('
    'wr%wMq1arA*C@cV17^<3WhK`+Suid=ZX#!6^$uEo%JZ5)=j>vvxU~v_4o+51__v!)EmQE6YUkpwS5hY-^<1IaI&n027Q3xR$BYw^6A((Ao9CU!ec$vxV(u{w'
    '+D{&F!Zs7bE&hjuCVW3uvO1!EZh8@DXg6`Q!AQP^$V~^6BP~`v*=WRSWyPA%1eX)++|CizX^8&NWMN;Abz3X%l~U#gFO2Yg5m4ruPq`Cy)roa34o5>v<Vp$='
    'gJbK?%of&Is*VKxpQ_BI-hDe=E>-u{s$7Q+SDM_XDIM0<<=V^iHL6^#*!T)fZjcmywI0{5_1~w)eRX>NvJD*5aGu%j7eL(V%|`S-%kW^$1w$3N9?Sq@Jfdg4'
    'd(vboHSP%^Ef3Id7d{-Jj<XeI@88eGjhI}dd(rnh4N^EBvgQ<tE;T^xe6$S$!DM9oeYY54S$*4T@W<#p4Bdg(<i*WpTW;CrZo_CcwT>CD9Js-WqVo{5Pq1R6'
    '2jHh}GZ@gEP+%EDeI5Y=KO7AbLL-iVsmHnqJv|ZiC=LNP=4gbtXD0JbqEs=gd#1ZdX<g^jtWRF(3*~stUco$b3ahAGO}!aKzr#$44!jpV^k$@b1=5O8)Du$6'
    '(kO{|8;^JXU^@KQzj`2>;;a5F>)pZM^SjApaWf=k`*eOti}3zE|Dw)NS839q^$U^6@H)N8W&`LONB;`qIJtP5tCjlZ-LB$~{(zY}-zywwYbP3KZ~K0RwVSgy'
    'Jq9)7N<u-*SU1-?=|4opjK`(>^Xs==becxRENo=MS>U!6)jZBHimbfq^e^skw-WTg&Q(GSR8$EbKdTP7rB8qQsr&BL*)Q)HvEJwy=|JIkZPXGn92V-OfromC'
    'emMEt>G|J5fcWA3*S9ZTb>IDRc2Q7o_r=-o3P~T2TS1lik?C%2sXjTMj|iOEbm^DZ|M<rV?7-JAPP;G8Pfvb^zu*0Qc6RaV^(o)oRJ(|sbeR$865M9mg&n$z'
    'KgqNGi}}d%5T`m^{W)&jt{lg71FE41v+RC0Tu{stKj19#6vwR}g|+GQu786E*#T^)GbDl^Msc7*+(n4q=sZS!4hOTVDkTg!(spm~+TwIri@U)bBo(1=3};a_'
    '^|0t2*jq?BHVkU@hOQ<redm-Lyf(rq`e!K4-`ldRqMC=(5E>-y7U~=hRPP!6MC}}Y@KuAS1E5H!l=Vhpw)^V&kg$uueBhhVeBiEj7~s4gGj6#jnQtT%G%Yc7'
    '<Yg>AEAU=%q)PXs9g(5H0Hv^Yp36jWp}DJZUoEXuNc?5|HC$1`UE2sCZ2Q>@FLm=_5tsN+8A3-q3H>9R=YlQ50WzyaGK7t_>x3SvFa~war}^1)L)rOhxf7VW'
    'Rny2PhnMpGf0F5p*T=#VcQj`1&gcumj`&Ia@ayY0FX7z5(e+&xsfa28oxk`M$k95>r3iYCW!IiceQO(1J3?s??FV-t<(d-BLSOu~WLxHXNh%pxlqdI&A0mil'
    's?TAuK54ZsDR-E10Uy$ytLfFB$#{|oRT3`bgR4I-Qbzzy6-A=bR9iN$Mc1}@ExNqxm<boF7k8WHVAiEQwo+9urZ;vAr*CH6)qb!Z>{W1bCjSPlm+r)xAt+CY'
    '<={_fkph7n1wkAfluKF(40dUMjbcp5+#~g3=CG`#8k0usU91EQf3_G}u}hJ;RWIg5S0rknnv-{hg`w2fb&31756#b|Z9|V9Q-MydfIakQF{q<6`#GSd(;qwe'
    'n9E6+VUU@KmE~Tx8T$WBRUG#1n<?V3vaeOcSre|5aNk67Syv@zE!GniayBcoLgyCPU0<nhvugbJY1=4EGhU-&N*iL{BCRe$waCL{3G{(Y;Ktyl^=rR#R24ee'
    '5xVt2E2$`SUg@CRYOi`gd@N`J%>S0nGNpGSl^DYgkWUb4&d5)bTDk7w8}e)WerG459C8m)a~o?!KSy*Yga@rXQn;KUI)FH8VnDEV-lXWJ;aqI}a3PX|WE)C{'
    'yel(`5F^#tHpjoRE0iA9K>SDN?1&lN566SaJr1DXo8qU@E_!b&U;!KnR>qS)w`YfFDSUB-i3k=G?hbZ~{ZD7g-oqWkV^8+Izevm)Jw}>dRpWpe(hm{nQzr#9'
    'osZ4mIO$lM_+lNJC87FgO?vMUsZW$<8Wfi;P*L=w84J88k5Hv3L~|9@r3C`Ux!@hBQ4=Wsx`#NdiH0#?&H`OkX{`N)>;YQ*-Nd-A+8Yfwjb3Bz4NBSa{y4W!'
    'JX9e4v#!ZFQz%PQYzm$HM7i~<&BS`>_=Rrs#Y8V$EfFQGM~v4YA^6a+ixfck&X&f%!jY1*bF)v4*Ijk{V0dw(u|jfO#VG#&L9=E4oR4LrOM;fEaDcInE#BJ-'
    'R(JVQD+>iR5sm};i+v_Z!TK12P?}>g7e#A_2XE)|En4UaP}%1%`PjT=&OPPn;0XnZ3_az7&X%xI;O!yveYxyN9OPJn|CX-5p}N7%x-d)uyIPnO@FrmR=^54C'
    'OzLcj({K*o!Km03cBNozph_fAnIaY~2Rd}?Pb1fD^`Ud=1%F~+9NC@0aE$b>a{6xE!o@7oJ9`v)@5QH;qmvCOUoE1e@|OKtbxvc)`xO!IB=ppw|G24j>vCsv'
    '0+Efi8g)_@Z&31&{t}OEcR7~oHZb=yISmuMy8DIU0^kGqOS$ScSxj@G8^XOHkCjyIKif5lw;48AeM*eEIHs6<BCMzm9~1X~b@!xDKYV~(>i3b%N)@*vExbB4'
    '>qaM=FxyM(Fn3(%z9Al9DMszqZLvW$N%`uzCvkbOu98eF*5Go(W(pk9<Uc30w?Oo!VSE$OJCJlvF*d#^>&>4MV^^_OIZ@Q={8#vfC@#(S3|Y@BB)<>7RzkIE'
    '{P#(yXTO}jef{>QHaTX@Z|VfGi_2MWs2G%4Z;&Z@^ppYF2t<MSiV4BdVO}>aLd_@{5{7)@7n%=lw4)z>{d?5hO6cD$Sa?)E!5@(+)NJ!ZRSJWws$-C)YCEw7'
    'x(54uIi9oYN27kg?NgZD|M`9wqiHCs+<b(BFs2+B-YxG?Mx-{jTCsKyF?~gea?an8+(U?W0!2q`6poZ!7M9B21W6tUsnjo&*f6^~7ZQPeu)Lefqzvu2#u2(9'
    'R^fiwq(N?Pq3Iik-D*V7u{!?ILbAzor3!#-9;1YqF)N2N7A?tB;QPHDmctJfc456KXojL%z+6qr{zr3o-5ZV)4hhU==)*(lZ?92dfaO`xpGQ0OeI;mWJjDl!'
    'bX2urMbL){NLu^#Rx^@_PAlMT3)ZvVYTRya)^~SqV~yO1!JmDKa9{8u(iTx$V@I!9BdRjv%6oxiY;quBF`s85Mjr!2|ATAw`)1PEX^6}&6Qvdj(e8H>%(*km'
    '`Z$DvUN@G^85c2I^ggy=;(z{MKXa7o11=gm4rwSq*jFQ=CFC>o{NurMIuXOW&FMp|aRR?@ad;?8$L_vUy~4-8ZS6n*ZR>!K7DBMX`Ts*?XgT)XcNeF>GzikK'
    '$j86cKwv*@(NT|^g!5<BbaC>_DOFThQ*(=IDtNmUZU-LYGzJ)uYM@i4EpV8HEw{_6KU#Fxrfr~CrC0qLa%5gW|5ISLz9s~cNeX;AS<g#ZSysJuq1B5WGz{hS'
    'ZlqpPFH|SQ>|m)R3ISYGkB9;Hb|mG`>J&`{iq4knnWFIby}4!yms6m5S?}(UX$xuRMp{xQkkF!un5fmE-gVYy{w&L2HNQIk;q5qf1c3%5)DP@jDNm^C`6g_k'
    '!?3wEe+AEGozTa#ZAF~e3O39Be}4qab$;^Vv>jb*Fym2H=g=mG$%Z?8_%GD`vI3v@5Zs(9D=s-y!e$((OY|4P&P8o30;wSjgLf%xmjAQc5R6I;Iv*_;I<%ji'
    'Ptgj1T3=Y}2$&MG5cF=vsnYn6Qa|CU6ddNcK|ZF|#4&W*qfCPmrZpF@S<+;&$$|Vhd(iYJQs*ycl#3G{-H;+2odPj!P&ShyY9_AW`0&lVh_GmVF{$IfY$8xL'
    'RtK?ooFQg!5BL<!;R#LL_Z|pIxz1VI7!J5UA$C^t1p;%-yc=>ucz|cUzRUhH<AD|x)W=PiSEFGcrr@;Kzo7v+%a(mYZGrY;?U5OV`C=+UX1dF1#{!9asNnCq'
    '`Heqo)cY<vVDnr2CErSo!khH25C<9i@O={l949le|40|c=v)j8<btyONE0!-7K@iR%?(WiFShaSWe|vag`Q2`#%$`QDWerN#wALG=RhUX))gIQkKV&dW9p%6'
    '`gS_YJ`N|#Ic`PfOL>2g+Js6V@{+x;sKVYXbEcfmMiiZmGrfa&M~YjujHay@LX`s9depm{R!68Tn3KmUZg`lL8Xem1&nM?Uy?&eUkC&%Ep8WdeB2lmYE0zjL'
    ';kRHojnVLWA*YE>2Xt?*Ri|A-X|E)6Y<1dOppUmcSTsoWg-so<I6iikp*wBHTxT}Z3^nkdt+p8chU}&-gM(?`Zpeg+xYm@Oz=iW3FKE2?*imnrC8VE+B;x8B'
    '9`yzTQY*uaIMNw)jSXq)P$I(MMlw_HPwseE!BLtM2~wfV10dQr*f+*Jn2hjIe>g`5B#KTf)_C{%Hjh>Sx(N<_o-N4iMzY)9R(&t3*0vh^F@aD<`;F+1Mi9LR'
    'v1@+lu-a;Vwp!1dEv{Ke3|F>Y-^I#y_VH-EWU?e%_X=9gX6<Nun?6PAgma4|iJb89Uy%znT0FGZLpxsm3YHBydyzfxgWa8abBAYfdmpQ;_9)5l0u7McFd8<='
    'E+$xGbGzQ!)gvJhH0$@47`CC;dfJmgsv|+L@NlYx8ZJpPx5%NPh1Z-O@`mB(k*qUtH%405K@MeZ2wE6tBb<-rSU4rIX$}V*I5(bPgh_R$wb}YB$WXObvUjk@'
    '%hKH2=LLyAf^gZ|+?N6etpk+zXhDcAR0eA%v9OmiqBlq}NLJmiH|%|X)s~}SPK#KH31nlgg~{eYi&e?{u`Q#v_V@WQG|yxUt-p0zEFPp14fV<VXLq)>+m+4y'
    'PZ-q#;W}Un!pBsr9VB)_aN#K@0fswcI05MfMm<g^P4f4Cz1g%#=v`LFP9o_OP<uUGwEU2xfV#tnGr7ejq_Jm+By0w3MUoq!#rAGE7;v4`teZ&zH6R)-iSl9-'
    '$zM)sm&`JP+Xu!&4jd7;x!R^`AxW=<(@gWxhNZ59U|(x)@5LzT)m!+ZY5m=Z57}|pIk<F?uuh^0>O2Wq5F#<85N#c20^61V1lTx#pTPvd0dDQrx1pJxo!uDr'
    'BGxERwi~<9i`GGX3x2frTG*v#y-5V&0L$v1+XqM=e#vHagsoF2(AIr00#qg}r#_>yqm&*)o7Zz&mUe4vpR_0~J~(vN2AGn(-y0d6E4^E3A38*pTl+&)3HD`('
    'z)0KXDO`&9WZ!;*H>e~RP!E4P`Nc$yD3fN7FLyF$&L=Qotjclt1jPp6W~O8inx!z6|Ni>zOA2V&YM9FT8k}4!cBMC?+m~$EPSjD46*Y=8<U^;bHi;H=kn0BL'
    '@FwxrO};?M7Q`jiPsSkm4KScUSNd5H_a(Zc4XwzhEF;J0plpI7@V%<j^g$I>by@KtxeDDbWA#@22bSi*4qcfSgV8R|H(~mFdeMDx@*`KL=1f=UhHw<rr%V5M'
    'a{lw_`8(WEe>>&j_?{p|%Yk)Bco43m6)i-|>iU5QmrhAW8wv4*^at`XMgAa~Rj*R?2)ij-ITU^+kqqP4C_E)nW>rn)Dd$Tc4)_f35K3&q+y9?f(?4}`7n44L'
    'A~U(mo2b9O%^v1eXQLYTTBR`fYqafKY$$AoyTp+*K7Ik>vWk#zwkzq1uy_(xee0n@dL^W4{5ov2S4D6f1!j7ZeHf*;hCb(_YobcY^wgB3zy2s&!C{uP=(f~!'
    'lqj5u$6jrr7~(I?F^-I3>Mi?)X1-aEW78*~MZC5VfhZ!vpXaOhPptEwX2sEc%?%T<d^aThhhRs$ZN)jK4)J96x<p{<u1f-8%{&F-)_5?J6Zdh{$gQ!~a5-S_'
    't^(3G*uxws?|d&=#ALZ}SBcK67$8aCYXYWVO3#`9rEH>fJD`xGNj`hKD~A1s)h}Y>0cjFW=ZvfvW^wR}Qi%ERr_yMy(ke@`_>VYR{8xMFey4H3^BU*>KvnZo'
    'Q#sg}`JS)4ex>G8D4t7iWzsmdGI8cmsTwIX!92E75(`0asHUHS7(aB}?lnO8QJMpb%X>6X{IaF$5h_!cnyo=9`ePF#Rg7Xuoz`8i@(H1GwO01VyYgT)%w?Cy'
    'qgTU6@6o{E8!MZ$;w?(a=E6^4jC5{pLONAFI8-Dzwm*{yIwc<*Ipt;R3v)S(s!CGAn;0gXe_qyslpRGD!@Ama2+uy!3BjHIR5cG0ZjV#t*rUxY2oV~+6iRVV'
    'MgBwMD6nteERF&z3&&9aM@MrBf4i~;yda9(rl!^px3H#N`KheS`jtdfxQ30uJ!BSXZf^vmlEkaplBW{dN}kx2*qhDV<2)g;x4)3Abzl9%n$}XLQF^kTlZ;DD'
    '%rxbQiPaIZz^Hv_;ov(4C2Pk&)|ylhkEY_L?RYd*tvzMPiKmVy>l%jAJnGluxTca@Nc~Uk4dL{RRWyk-^9KW`-m&4d5wqFAc@%Q?gEE)+9`}Y{-pwXp_#69l'
    'vg5FInYCGza;Qh}W-l=HBabGRZh2MeW=3HXFUdCczqn4i$=cCpyms2weCcb=%$I&t$SHg&Zio4iHhVHVT`z)#h`)T>^X4qnTg!gErmvdS(7(@D4LkA6f3=Aa'
    '*C`=v&rtzU(qwi6V@nlE*(yc_Z+WzUF0z4*K`&Wd1%Shtx+d4xRwh@&u(g3B7)|b@*A05jxGfw`^pSL@sE<s<2nU5Y2#UTDeL7o}P`4$iN~!O7E%I92h&tLR'
    'UrB>_&umO0!eLI;D~eu%YPy;ryy|cOZ^%ZcJ<qVEdR-YOG^~@Fquyu+jX#*)JJDQop4#hd(Z8Wy-)Ev;))pXTR$#z+ouyW3m|5*6i;;~H79H&$)82!Z9pLAz'
    'H(z3Gm96--3=u75h?qOJ99I3Jaf$-1Xx7Q#LgqAHVz^Qi_!G|>tv7{Tp|KQm3s_!m-!~h3^=4}eRlW!>1r758qtYI0{r+IT4rTB?f=?x^#D{_h_2$+AJ#IDN'
    '@g4MK41YIU{A@@3UL|Vd`|T~RqS4TPj=T!koC*blO)@w7A(~@Mg+T5&-*4?p%?gJt`hI7d9&PO;yfAk?is5VR&|~Z^Vm*Do!+qLm#O7pRlo*8&F(B2#*|?-9'
    'RTD=?fD-9q7EsgYS|rL|vE+zvo|tGB%D*9CUyy@hTQ;h$r6m?Ps3n}qW&g%XSwIRsZT1yg5lHr9JPP*|hsY<4>?{baeuW06(a4a6(~qcIhqF}uc<_8HZY!Hc'
    '$a=^-Zfge?8!ZK`hL|3=_r)H<mPgw~R2ef-;fKIo(RP#Umb>^d8|w2dp!If#tP$JW2l1ht1zuG;4s4LyJ$Q~=v|8IrcJ_B;-RADDe!jK44d075hkUgqZ(B(V'
    '-rAkjubRpJehWTyY;jZE>)HYsRnazyTd6;|;;a-mO<>fUyY&W9aC8)HHnyI_f47_P-`3Xt^ZP+ljLm<9UE-Jj>i%%@jx@ZY9d1W>K$M2K4NGUV#O(-=gsmxV'
    'M=*M=y~l4G!CRg*>FsEzq14pyA=O1XbNCKPfE{K5?;DtZ&-7DUMlkh*$O+R=u;Zr~TdS1O{BV9tdqc@0_(X!e<)<Z_bWIa)PEQaT>xF1yNb>HEC?SBaDT6xj'
    'MHPx%8;qfkz$Yh$kxo?NJ7)OM$lRSTwZ>C}TH$A#{7WFunc2Z*85-Dicg=FsO!^0t#7n6i+^;T&mH?z@^^2qClGX!qnVxTEret1=Jp8?xecD`!^6t|@#e(W+'
    'GiC|9(`+`J49GtA3^l>moBiwez&PSniZ40#$qW!`I*tfM`{cz1xd@U%4<7&3uTlbYifjP^RUWl38a(<(sm};8Lk0gqV;$8OJAE=oUYi&)RaOO(If*axL6BPR'
    ';?`EkT~Cp@#5vU$w^V$fl8NlVCrd8MNn#?$3R49Gp?1~~AJ^)9)clgyT?R&A8CTS~vp!J0GnUUMDE15rzTWRnEs35&(qrbq?p2IfAWI+YAhYYC38q?9Fo$Op'
    'jNc=)Ev%v28?d%f%l_O3bRe<Y=zZ#PTmvfV?y}kYETzz3U*&fNGk0qzKa`;>Wo?QzoA>I-Uv9vEKo*<NwURdtzV!1?I<=LMEWR9a;c0;u+M(VJmRVP8vc{hl'
    'uG$fZov(Pz-zTEswJwrBA=b>F5Us^~{GD0slI+jIYGqWJ1Yfv@<)LMtReWGu$4LWs!4ZOzI#uWi{`yiV*Za-?dnNmyPA*Q{M&d+SogG=ov<Z)&SpvbcsEUua'
    '8|=Y|4168R-S=h#EyQ@vSuAbirBio(JUD(TCp<`XOeLbL2lfuk?m#->Ex_XNdrEPw+;6BiT2MM<_Z1eTu;ASHP-6~$(vEs;9hZ1BqgEiPid7Dz%|OYDC4GhC'
    'k&~myG13*K2H6$5vku;~6QdTJ^xU#tpA4Glw#kB%OdSbVRH+b-A&FM#BZgjzLpYG*g)cm{(Q!692fpa%Qx>E+=IM{)^>P3FIo$r&^ZV4-5XX<3B*62_V_puE'
    'JX604@cYz+$tY)^1&iIco<1cC3h!3*PdiE#7ToT^?kY^nb)arVQx}#H^h!TcM$q3mQi8P>uACr!D82>kDRyRW9gBQ%3Yf>6%?Z);U!tm2W|dNle?~dKkz?CE'
    '*wGFkWK7`7Hb3@8%M5M+!YPpkh(Yh3Z|!woot?k_$JyI=1+64eE4G{qur=8t<(tEXeOZP0l0?r|qr0FKM$j%6=%DVFf}`ydH|>IkF!rZ`{)FAfu$UlHodbvc'
    '>$$u8upr5~!|})JkZ~3IN;W`<Kib4A(%-S5YypDA<<qsow1w5hUbtUC=tywBa)P-ltK`G`WWr2zp9;pbqx_T^L+aJZBvjqGoJxhu!Jw>hd37I_*^->J)iFWO'
    'pyBvE@X~5Kv+i;-mzAI|f;4{Z&fwjO8&<VRTrgaZcs`vhLP%?=FlQ3_2Ev=7lJLmVvH0TCYCn+P$KG(%yCNhQONz}K#5{Zt@|@7$LNDy3GRK(4bY;^PFEqE@'
    '*_5wg*AOcBOA{)lM<PvH1d2m%cyer-m5m3k{Z<J%F4_?)UlP+UI>31Ya1|Y@7B4FzqA%fCY&}I01+&WpDVXPdm)nyjf0x27W|>kSFYHYSD9ICFy*8X9UXWbQ'
    'G*qOPNs3UK0*xDm4+6gClqsv*DMPJU3nJE6PSDY~1Fm%;TTt(HZDUuRt}_{+PN`jyXn>v2@lo?l^#^9iJ{Zc!(W;ui3t8{Yfvl%eEZ3@Ya91x6>vwQjK5&k?'
    'B>KP*yrz#irOt|!g4Ub|6A8*G4YU;KFUdEltbs*ysRB)F{V%lk1%KqUEuM?eIZ*F+CvS|o9R)m(Cuf1((bKH_md6y#SQiiqSVIsH2fU^OhJA-?{nL?v@<Xxp'
    'GmnsOR_bP~@qH8ROnCPHR1J;Qg>`i_Df~|q5B<e#f#-a4`Vhf3_@%2Jbhoy48#`O}F8BkKJ0SVLxH!K!`QgoJn|-S51YvwV?2E?+8?gIGsnAs!Kl^n&V0cpk'
    'glRRR{}EiE9fi`6m~d^@eBi{_TamTo5qt1Ol)Y7D5EQHk6GC-8BurN26@UP%KzeS+oceEmQ(p`*dpou=$Jl4WLn07}_Z02OVRl&B9t~@dEjSrcYAM_p1_0{c'
    'WW>?Ieg{5O49CfCW82`;kog$T8^$SLXW2-Sdk>@P!QR1U19QmkAH?i)HIMe{`;p)#VH=SF(xIPCuIJ|oR5GjoM46|mTU%VsK|`uhkytYGPDSc>^P6v#7Z+XH'
    'BPR688)3D&mta52@Lk|76l#WmWOj;hWTNW+I`!@s*Q+Xar?OhzDzCTIpo+H&D#q6;Qt5?CYY2aN@k#wf_j)*E#dbf8P}^s;wTCAqjIrEiZ9#%hmIol)6mZ7E'
    '%(mo)1}qcV7SxK<&08hyV3iXxQ{^V>auRJB|KkGB!Ak`l<I5<fN#E)Bg_Yw^Cefki_?4B%g(~qvHQ-UXgs$SH=0LhZGOx}F+CV^En5RWd4thFKuIdDQgA-2i'
    'Lr#l+1l2c2_92gX(;2@t_NsF;hhp*dSUr<$-RAY&)S=RN{1mVp{`0bJ@+K5RBL2G_<zIZGq@OR!vwg0_`Oh%}PsQr7Y0MK-Z@TC4tI!o+JQi5dVwdn5zD9RV'
    '#V)A_Fhl!W+kXPPboSfn`HyeTevhhCA{z`yD4tipK@ZNG+i)G7+}y#tA5f7Pol*A5lPRV|thY8B%rd}>8w{9kZE+|#Cljckf8hIxU{eVGf3wl36Id*25D%q<'
    '3xsnm!1Z&GmoT3GAw!szcj$*}dsJctHYyCE5vmWQ;`_;x95p$sCMR}eJfX?mbd)VJRM9Q!gC2SXQdJ+bKKjbph!X}A0exKALluozl>Xw|o0+<2zj;^h<YSlI'
    'aPaDdzqQx`e}}GNcua0{^N^(luTXRsB2aWXnQu<szCAtfzI}ID>GlzFjFpO&4&8zkx^pX?OZveypwdB*H2Tf;R20!E(5qKiN~!QAP(eYZ;_KBbB(+pLt(3rq'
    'xXw8x`MwHNsTG2VuK3}%RQY9J+->-$t5MfpQkKSg%DUYo8dF#=e??bVmBH4bd6}5Y3T30ONah@@(i%q(x7rF-y{^cDRfg&IF}%yi?U)zxZfONUd(O@vqDxz^'
    '%Zmp4!`VxT9!^5Qnu?98;B^2!=Hvqj{U3WDTV&R$$=%8*&s2L!bfreDDD!AU2BDsrTG9sKvn%_VP8fj5>Ae^vJpAJ-_Kr-BbIofX%vdPa`#a!Nx5{~>P!_}r'
    '^A8n23nJ+aIrSjxv?GSdiMq3cz3$a=KyF~zzkGtiK+|34l!s}8W!*{egDx3xp*8Mem)@8yh!hvkt+cO(ID9`G_eQ{NPUdq}!5|wA5$C5WmFrD{z}GITiJz?k'
    'vR0{jwb=l65T?Dtyq#n`&{jm9C}BAAqSmi^?}_mZ9;iUfzMOCPOdW3T$c$Yp#yE}-DNI6?xZ}ih9Nw5g)Ke;!SC+!@#TNm+BMxU1?i=EBS)2GQs*W+L6F!Lb'
    'VImYDCYOiN6@x~aC>+}cgf%*|&Yx;krF!72E1P+nkpyhh0g=7kp{t>fGmE>}tNl0-0#)ww<{gikBr)S!iR?92I?cgNPgBFvimvJMvVw9$B_WF5acH}q1la%`'
    'FJAaDheq|l5=pN4+;nq?Mk)^-8kr4E8O`yd+H&*Ad!VXXPsG<lO`SQ4R8oY36_iCYD3=w*npAB5*(*T&3Kzfwiw(h5WR9#0dtoFnrAbTa3liqO5-~K#V?R|2'
    'vG0o~z`VQj!#rH&X%dL8YF!EBY@F34dDVC_u1g|$LM}vaFYTx`zR57#8?e~JPjycEE#`k>c~5{F$0YTHjm`PQ7$FgPmmca$Hls5dcyD9}AW0%ITo7_=Th19~'
    '3SG=dF}WDtWf(WISWYF#NxC@a=r4p`suOAz!-whI@yML_XW2b;ulw!|%*y}%_4M5ZX}4QjTisdqVM#!>`11F&^S_;*>vudK>N`j41#$wc06M=D%S~GZcv)71'
    '@mSa$3O>Df{f6^ERd<q|IH~T^fA{3SyYvMAy958VxsUm%JD}V%Nsh_6npb<U_3Kx-|7-lSi9eeiuZC%Faf3--5>7!e_iDl$sXN=*LZ|$@<$|q2RaG{*%^uQG'
    '@9t{Qi?E`0Rd))j#7EQtJiktNnU77bkXrt0I7NKP8!p~#V~jBV$*w)p6x+$G4v>+xJj9;J@h34PVRr{J8q}?%)&duPA^H^d%t+}K^I!6)VrZY}f6xz7wkC64'
    'Qj$Ez`A=jUhKpfuR0)7RE5(nJv(gd)>JSCy)MqUJs?u{&hMe@0(&bd>M@7=*(2Rdd9?11TZMu%bQ4wow#Xlrg{v4hHPVQHU)3icK(JS^#N_;0&J83|fhC%(I'
    'uEga-{|gX31c;qaQLJXf3-M7?vdweM5g-S;7hNxfm_*ZI{}$b3p~_9Q;Jv{^LRF>R*>0;l98Z^c$@XT>W>EqKZn#vR2l_72)1+y7?_)Mf^+x7WPu}E89V&D$'
    '#qV($WIC@^8lXz-&tuIiibS-quv})!nx5i`uKFA3`SaFxtr<T9DQmBJ5Z7t?49YnTyr#Q)9J0*^SM-G;+x;E}+#<`H%_!D#z(y(}!r6R|wl1Lg<T<#BL11w1'
    'IcAruf@y_u4%}3dPRt|Kc@Os%GS>aklFlHpH<4nIHf`6(F6}0ocN5J5Tl>}P^V3RDE3Np{<WjF6wVDDkY94^7bj3;NDpa$qNT+5uS8Hm&EbfxoPqa1a%}&C#'
    '-AsT_Q_teK)(nZ1xNvFOI$-+P(7EyELt1MRGsulH(Q8)c<*e)FtgEhAY#j~jD6Q_+Rb}zB0#5z1VjPKAkvCY}v_F|XY$A|0{vmmn)h?Z*mK{r34b@w1SQX&6'
    'X<a&r`lF+(G=+(EaY?xL!bAIQ+En*kN>_|9p1<K$qF5_pT4=G<?E-_Wr;16{cl~9>zU5(=(`FgOmthzb{h7@COIPF-_4K<m;H+%;kU%|aULqnPq^>gV5cgE>'
    'ZqZvRwX!UV)~$0%&Ex(&1i3g33&~tamTL_38V<}Q++@q~d)WRB3m}e0VN!6}@;zK#DL*}2q=EY_=lB=6$*>9cBKuBVWVvM2>&~^+BJ4v$v^#AcpWYRP1r^r-'
    'Pi;cpY4cQR06A(_T1DEB+GJv4`3-Z!$FK%GSh8#3l^n`pfK}Z0Mz_SUVO>huO741<M174!gey)w8P#hfwwMYUfYqvd%VLXM#LjiLoFRCzx5Q8swXO7TqvI|%'
    'JhQfpAH^y4S-gxq$=|ZMm+rk9_*UIRT}@moz9j844PV6<=lwV}*AO@o?k=<VKO%j#(l4EznETe(hd<>eL-G>5z04LB%@?yQs=Upn7?Yv3ADT7cS8#r6s&hxF'
    't}mb{bE!J<EEYizP=?FOi?cUxPG4Mf?aR+k=$Fb$=SUX6rY$XhI=ec2I)wrd3>;p%r!Om=0+PaMRw^$}@S==0f33MJaseLBwLNQ7acYd(g1nlFvFZubC)v%E'
    'F6S?jq=R^?-oqimmPmpN60ZsEdNR91_om@sOfE`;jA93{-TCtRde|RwV3xbsu&{M@eGcuB);7H~0#9##3j$APy-Vbg%b@1A^tk6OAb14a1MkpoSzuFw-`ZzI'
    '%CB=$Fd;KkQft<rPJ5Hn%oxvHD3kC7t}2hM+`UlLRy0Y6>EO}JIG6M?E#91~&PKsuQx&JHzL(P><t=NA+;`SjkG=FTss`>ny9TJ%<#1iE4P}<JG;OJ?NvqJq'
    'iq@okJb1nx{dU@>0jMlHT3METn)b$X)^l-k^QHhH-A@$k665kO5Z0b-(}>AMO0<XGj11DiRBuvXCByn~N**$>>PlIN76l!exd%EaJr-d2oJ@oKH}}xv3;u5l'
    '{*RMzz-F|v6EyeXMHB6G{Bo}y^{}$*;q~IiQOL1mHO@HY95x1@lNir>x~s{OGZDO$(f81D&Pi50L>|gRFkQ|t3N4GO<V?_%lwGJL9KIjpTyRfBm%u~Trhm>`'
    'y}<Z-QX^2jEv1H$eDqbZ-1ip>yi<UrSmv;^i;$WVx^}~vtXYr2ZZfRSz=~9N<IU*xLiPYdXfZHY#%`UQpM_9=bz&GbP=mZoG#Y)fkmAk=u!=K8P{JK-juI_4'
    '{mh602uArDfq0|8<vk|E;EyTC38HiL<}zkfj{bJqJ$>`~r`PNR$pQ^ruJ2Je<kzka6eM1#uG#F8A1SFp^&>V*cA*_i2;jb(+)AM6Y4;u6acGqi?y^l5;tGe$'
    'R@$^7D;zFc;b_;2374hP_=v(~;n#lS3)jkla#XJ{|L`qUeD*v1y-k1rbawXc6n<?{T&yd`sZq00)YUY4&Wf%SrJNPXrj3T+W;5g{ZYJ7kVeRnC3jNfS%Gh&V'
    'c~3-%Odx+3)gWWfQ^Yp$8d+kn=rI3Mhrt&39!O_MRX69b;=-)%um>@Vd+ga)$>rhF2H@5%B9wy4e!&uI5<un7rC?XWj>a!>Tp}1HJS->LBdYNv_6b4U_N{37'
    'xbHOO$LhoU4j?!W@r)T|<mE{xN*nfYeNy|8u@_P|;Q)o4iLLcWFF)V5qmMMJw{ZB#oznJ3xy9`%gZ{E=ZM~3dX9p`hOl_A;X-u(yaKhs^WaYBr5fsPr<%Deq'
    'lvHv!ryQ>*TaOfSo|Dib6msX`(Kokvclz5i2M@3Hh2dR@b2SO<s60!l5QEf)MVIY2CvRU?kZ&=OV)UHJTP0De*J&3@G1f#EwSpu#wCi~)WzREe{<BEYYzunG'
    '`0S|v0rm9S5a;u?o2d%1Qo*F$(hgIo=IZujh8{C2{={jmydBa}hC;zGIFm1clID#*nf55h?Rg38H5N0LxExSodAG3fyTG0m>jUAypeuU?F~s*8jRt(T#s5%;'
    '98lN5ar7?pB8&8@Q$4w@1oByM#`_}V*HxgeVcz>frJ!>dZp=DG=@o#{MxK{=(6^Wij-e8-Cz#iXI4a<M3DHq3*@S4REZSGg2eLb4!ckLs&Z~%G_u>Xb&v{$8'
    'J!Fd&#MS#5va|@Cils1J8afCP7YwX6(<+sY3E4#AX(uuY#8I77eaw&=mJT^>;k@hA=nXTh*fZ9R%oRsV-7!qA$oJv_ADytVUL=Ute$*Ral8K2xw2qf^;c}%m'
    'noNP=M0rNdBd{!b%m~o3L^t6fr~X846>1g+`gS;tP=!I<=S7KW9$pri=IOh4FMd@#>o&&m^_Q7?<#4Qv?s&qQe`UCbM{}6)QP!0?blxy#Qy1q&c-9NYnjh_8'
    '1kJAeyC?s`^IdtqE6-iSK2(iM(IqtnVM175xay7zA7xiI{lvhvpV;cFJBPxu(U7_-kxvh#4uO9f9ff@7g&ZStX7M+!g56@B*89-0A`3W0r_AbaIq?&36f*o1'
    't+;SZ{{^3w+V;b~spQakptSgw!vM>63*gIESiY6NKpK_08-!g8xU_OFSkV%l@HDi;l=l(HiR8vd;VXubLhdJI2;~5J*N*^eb|OJ=Ohk><m>eMeH7#)H|H!6V'
    ';&j*sXxJ|5`HC8mCc|y@;MKZoe|2FlCYKtla<nozk6Z(%<K5*LE45SMauJwR_Azu!o!@GfFilT!jpegcU{zJhR%6`>dR^#K*NBOW!mSc(E37m30kRw756Z2q'
    '%DLRLvz7|!c)O*RoUZpaz7VI?Y75m}2O;I6zKen#cpM!sm)z0tl}3eDSzKi;n2kRY4$n&SEGk1I#eaIHMbsfv8n~1k%-9wOtza=UXTgqD&zt(W?gB^Fz@{YU'
    'U)!g+T0vMc6j&@ZYiz4@mA9{Sk~oVr+H3BqWl4zylbDS^Q96U(w6^rxaqFb=#DzUhxstjb)JipRl-Cn;tuS<SIQe*~eyP=C&J0Fe{ggxxu~^Zf2isa%b`_H;'
    'PJz$nFHd@1c-wX?`-tVyZq3)eHDtEz3W&xd%!xc08mMazmkP1hd}Lf(G+ykayDc##=e@hvSQxQdN4gTrZtb^rDTQ>@P;N}N>1assL#3VvVv%s1=lx07Q-XE4'
    'Q_4B$KCYMq(}=PGn)f7va>X_u)hVgs)yes9z!T+aaXYL!8?b<tRbFn#DVY}6{7iZ{sW$Iw9=ba$#=H_p6egAVrh3O>=8(8gIpX$!oI9QCL{(R6QIiv&So0II'
    't`%%?%ev;9y@=}k0n{sK-%^*XlA;2vbXoip^UFl6SB38A%ao<JP(#IPfs03~1-@~V?2A!vImjZmQ?xj4x2>{XST-|;;?QYMqyS|*nW6$BIzxp3TIlbfyX1RK'
    'N{JtqLl8|chc~cK^XGkPu1lF1x?Bkc2UiCf(YqmM=a^-G0JdrO#Yy+a^Ru5ZV{(IkUYtdEp!tW!5UsZwn^NHA`5ER@*1v!F^~WDca+hzAsC8eS{2hhpCO>*{'
    '^6nKDXvim8qG#<8wRH9yiQS(!-onDa!i2jZq}MT9_r|-kU-c7uaC-8NQt~z#{d?p0Q~q6VN~k3@%KbE0t<`N7*bQDQf@5r}^6xHAE_AY9>ZIrvK5z7U-T8fw'
    'ax5Y6D*WW*V?7W)HyfBo1nzHs5nGNXz6Cw>6@gfWHq`&e-n)0Tab^3W|KBmrcc>^MSE^7V5@5#&%HtB7#2&GY4>;{k>uM-MDvWF)2}yuy4}bSFU+Y<`N)pED'
    '^gijmlc1_q>%Hch&)?*d<iKgZ=4}yt#r!@-cbaDs-CooV;+#`kP-1s?*EW#BThxHp=I|C%CAL;h|2b#en_$9EOd9ZGGe9(y>b}e>w#9%I!1F!adBjX&7^hU~'
    '6b(LqwJbqEAU%LR7i0vkY0S(7PB&se%RtV1qci9=JtN|%B9HnR#YDDiRHBYH2=y1<JNS40i7DrnQS8m6-^bn9YYE(EkG-3*Ez1BxF|WGAZn!YZ8q=8K_WFH4'
    '+ikz!RwV+G8p*l@Q%6lEkrg}weX8N-J<L5xuQ!L|LH4oMi(^MM22*+sOR$)`7Xn|BUBO@kY14`1s#GfQvrc)c4VveCenlQl%-a3&2h{P$AB<(dS=~`ks9`!}'
    'c*za@@kcC<2!H%Rt^HvoJjVTN!_;WVjTKOAEP+s?)nI+Ha=bxO+KR-1R)_=DpBL;Sy^0!bg+CVXuMQba`NcVlC+7rUNQD>;%<{4>&gRTETViK;3D7yuho?jb'
    '3Kh`oAjk-8uTMD4m+XMS&;Z3~l{gj}iZ12iReF)SruP&suR(2d?DhptJaqwKnUSjznn2H(DCpPhcPBl{Tb(Zk0!OQFtdNBWxXJ;;gh-(_f7l6RS%k7<EUO0q'
    'y}&j$s2b;Klb+rN)0;OC$7TExM#g&x2gT2B)w6=E=XMjgM%<%Lz%(YL!75MkDrzyXxf%!OS@<$Uvgv6EqSMN)U4spS*u^wUvA5D)YoCH}+ce5Bvs1h*-huok'
    's7R~iHisUJ>PZR7cje=S&ilT#T~sMfXFGoZc(;|S0E6}iSs$3k+QkUzqXmEfgz722LT{q+g0TA;m5tn|+ZZbX#o@CUKcYPFuqe<XKBA8dt?Nk)yL@1xfpO3D'
    '^4GNT^&rQ!6mOn0n0{3^Oa*8Aq2tptW=r)o7UyqaN1RG5;3-Z9{6jBTw%{-A$zU;<6q5bfWXg!Bl<$bI5fI=SsJ=wewo9ZvMJDhD9l(Gs0{N4Ek0&<-Y??Nl'
    'r0mqYno>~`6-X!|TKGHlNPZDsmR!Bq8!;)OKL3wDxIb{AaQ%P$aod3FXvnU#Gz`HG<Yab#{Gs{;rE0Y1#&jo3tIcd24wVgJvw|151C#)#LT8ZKZDXI5iVanD'
    'H7G=6+`3a>!6-1CrxDW%sWRVdT`3ZzTUl~zHuOB;7HA|M!T_J)39%nM7uGgnoovo-4q_bI?%-uzEv)rThU|`iBGjz8R}4JGJ`+xE-*W)I;q*V8ar-e&Kv*r+'
    'NWz14b3RR(oUqoV60S+13q#vPi*T5*@x_k_C6<*MBG_|6azS*nr_X<3`19v4o_3!c9lbWc;JQM<_)7c*1JiwEMa~V(l=YFGJvIFSyn)azf#R@Gp&5J&!q%~5'
    'oSG2Tfeyfba695d+!WuW_CfZVwBGO@a$l>AQE)_1Be)UONQ^La0!NGAvTv6MM^HRvHgRHcZ82H&Mz)m~)s%`E6qRMgrTNNP54gy4L<QtqOyk$No_eBDbY2q+'
    'G`?0IT?VRfC|sr8O%f0>P)B$(K0auW(b8R(4VHNH;amb+s3Fqf^823a2s4U*B0osI7nF&n@iXLRa?XMk)K660<;EHW#TaO*4_-XTMqh+uY=9_q<?AOI55odF'
    'LP%bS3E&6j5dK8*;fwHoN_z$jTp2zv-vG-)E{q^hFcySbAb7(MV7+FU)=V_?6V`qx^#+{!A^rHA<Ir_?Loq^Hr=yLZqShf$2d&eQUs|Cfzg0RfSCx}Ck}_O)'
    'ErsNDJ5pCpu_MooR%i7l6e=85pmjXy?(S~vVx$Hz8^e*8N<P=|mu!7Q(_Q$kv6aBZ##mQmHoG(+I%`w}WxP?Mvkmg2=&iNiUApVLn3g4Xx4!81f#K}l824)B'
    'v8YstM2(Z&TZ>d%wb^okW%c#Md497@o_FY|B9o>0Y%FC#KQ>fyd5)VUps%%J)K|L(1*(|(POFG&q_oicd?oKQ*?4mVJ>JQ|>K+&vPg|4Okqf`LKoYvN)lRTi'
    '>f5NfNosrqnL+M;Ll^*5`Xj}dGSVa*+_@{Pk{(O()<e;m;fa$?t30%GQKoF2q*BGfvep@OfIfzpF~S1-fZx0vC=gUgN>>|JjFgL-DJ0#cM6XFy-(@^Kc^Z=3'
    '?eU;Bh6e391eLo&Qx<A;B~WRLrY;tuQRh&Au&rirwKw6(!Rl9c%SOLj_@LeBlxdDU?(#}#f|*9kU|R`z`m*|nIT2PPmB<m6byW*ShC7GG9|vzZwK#G^k`DLw'
    'DqPMxCdPbG`qh^&y$UffRv-+A^`^$wun{eBXJQ{F0v^IV?1!)VaMLW63U6w((0Mpv8kHp?KVae58>38F!qH}e=jN&`%ry~GTijl)bg?`Cv-BM9_S3fg0l!wq'
    'xmk!yU-Ca&eS%XjUJ2ZidP&y(ir7tnms`6Pt(38F$gOQc+Z-inccMcSN$YPh+m1R@oiOEEb~x5Q7~U7kG#E;`vi2F$w<cRk%?-7+NjK5l24}dPcUcjF@hvsr'
    'Uf|3qi!C}0ZZ%*=QEo$?rjAgf8<DZ{u6QMr+mAHmGyE8t*zL<jOpK<@zIRHuh$RzaHA*P987+bS49a*`qAH~^kx%ou3&a6TKIHs-v~huS(e9PR_f42iBh|v@'
    'zj2zEgaPDuOb%;~or0KYnXdvWR!qr^_n@tg5B4p{QlJ=zR5;*?v%KNqnVG?`H&0-q%Q!EboMJtN<5Ca@yF*UP(pGDw>&~*77ah}rG-7wSNbvk@L=X8AQT9z0'
    'oE8|-&6NQd_3jfTSU{EPDhW~z*ucwfq$O2ciG_gcQY1mHY|&$e55rXn@wvGwqCN%d=1}(B$u3}0<XF`U*ELU?mJ}9xjpwHm(l+KRRzgYf=JK{AJD8MxP<$C|'
    'Z}OmRo!Cv+2yLA}oFl)@2Q}vN*a@$yq6sVVxG9M_)t*$V5+afxGE@UNQ^S#p9Gok4@V;_aCbTtGzC0b|hli>SZFGvZ<f5Eo#!qnv^sg2xtyRuXr+6?y-yK@z'
    '!p4f$*&CG!ajeq_OKy>Jf=<?0+$QWy$nlY0?cPx{+e=waCviYqV2Z8CT+}6MTk|q1qT3{d$w5A!_sB8nEAkJXt%CyuQ>~%rX)4KO8%PPM4^weFm!drt|GGL4'
    'v@Y%E&g~_o0aoHYYJfx~Ls^b^{Ex+0i0*hBNRhvfE(2S}Pp}i{Y!Y3D4qJe*V%or^JhSZ_SM*6S`P)JAHyTCE+J|&AlBh}Z{%Wf5n$mLhl6{6LaJyQUZ>8Yl'
    'JE~!);NwTlmXnE(|M=`H$vMX|Z(k?RvejVXq?k53tNb4KIr7oy%Qve^uvD^96~nJ)IFW(XRTtv$hArNGlCi0g<U3HZ`Sc3cSK4;yp}FpULu$dVyw2;rkxwV('
    '7BMPctzhz%PpY73eRa8JtDs;YQB_k_TACHfnUFwMq!lwF9sDI+wka>y>*MFzX&a%F=A5|#mhzNS2vPpG>O2Cuet6L%uyfd?l+%_o6x_veo7#X2XzNe&-99?r'
    'f_X<DXSA!(&y!c(U)hkWem-+vzc_kBPafJ2w3BypYt#Dj`J2O+6bM~;`TWJNc>D}F56QPjM|3C&p9lXq{N)$4tJ3%8W1l^QzZmi-U!zkK{+4#BB~|m$t6z?u'
    'zxsvh4pyWJ8knF8fdK&pRuw-vdW*mGxG>@hA5cS|)f7BCdd(i`KOOvf2o<-WMX7)Xg}&skpa1J$2UM2ct13;;RMDIt_D{#Zy?XMjd-9rH(cP-OA;Hhz4~}1T'
    'Pu?6IA5v+a{Xn(PpB#3d93LLMG@bHhS<R{$!{Hm)NI!GMYMBC6pS(Oedh_i0VQI~Q?|wcwetCF&f*bAELmup^yCT-BVSDG}1Is;sGTZ9TGCAa8CB|n$rn}ek'
    '?)CPr^@0e1QtjoQYrp;6oj`?*Z@uj+j&BCD-c60r+*o;`Bq4lm!PF=_^>@*ZZ>z?8d5oD{DS~Y>^<9+&j)8O!dXEwlfL|q1Ee@o)R&ko@<B-oP^w6ZMh97?Z'
    '7xtdv%v4+pS&5p;ea0WzR&Z#lCx%4$skxT*!@ZQSgtrD95s&w)ntgVCwlRWklV}FAg`?kd-Lk!Ye@xgR#uSI|3jl!}++w!MtpgDxzAhhz<AGT2SRS#E`o*jl'
    '_NkR%)eg}|^bsSb2+E60w+I^jn#zj3C@^M)uyUj<2d`FQy|7GpSLogW)NOsyhOSCwom_AG>vuNjU`r?X<8(5=nq{uiPN#}bqSM}@e{KcBVS@U7ae|?D`j?#v'
    'se8QrqtG~X^Eq&Kw{k4oR2c8QS&ve;B90fMm&6X5SH3o7JhpZ+rr4tXpe82h*B}!}t+8GH)8{yl*@_^;2p<?r`ecV5wm)=~=L|LK#HQywj>2hl>1=yR;3y|A'
    'K`GC+bvh+-r;wA6Eo?;Z6X^%a@#RH%jqFbf^ddNi?~SV)tg{YRp^f?VT)|B3e;r>ieb0W0GZ=3;>I|LLpi`J`slY3Y*l_d;8>(QZp?hzjx7c)+T|*h{!g`)y'
    'baHfk%t#d34NM8x{>Der%Tb+oVQP}-8+2o`?kTFmp5*bhnDB7qtDPynB0UU8Yo=@usO&mohdr7*4~HG!a!`MEZG6PUd#fHbTVc%wJCu<rCC_`11q4$x5&wbp'
    'dY&*LW$_SWkoY{GPG;kToOz*=pmO*2ZsxObcB33_IBVo2L?qr#7Vetc<Z_5n;CMlcSB-rYSdvPsP=i~;PN+kq0_f?}w}*#Md2^5vDQ3`cDXuJc{7H7xX44~1'
    'Ra~L~=CK3}7j&5y)y>L(8moH5YHk{?)q|9KpdW1`8r^O2;0>erO}XM)`VBjfs|}Y_gTQvvl`0G_D!wZ-6~H#v{AoU$AzV37!E#Cx5JE`hlKWUB2P0j`*+kKx'
    'LfHk)Q7z&83;Av9=o<$}cSvx$nrojf4Ao>*TB2t%Wp!x?o+?%VL)vm|zA87l8GF46_MRJCb=4#`Bd~aNt|?w?{fr8cJ~rPX7@!e5l+C8VwbqZsRrzD@>~1N-'
    ';(G%<>!_B?waR&2tx+y1%{iRgeYqO;qlddYfw^BVX57t4aY{0-3iC$w9H*y-{V>lKz<2eoMlb=h?T1||47>*LwIqXat0b4^-8+IOLn*t8i4}Lq;&<?Bwk|$r'
    'Bcb&`PuQI;at42+%vm|tFnPx1ateP*FM8wKnlTP+8KW>+e=Yo14oFh)td-c<iPd$XcX2+I@p|2I?HX1#UNUdQenX{pZ89$8`dUB*2sg(v*Ld@<%^l&dB~5T6'
    '{I(Rn7><~Zz0tbeT<lHA0SMcKQB%)b<xYA9{w}8b_W;rmoK*@L`cmA6qS{f{F{bNi$z~}GC|=dI@!qzX-R*kH<cE5;AUe0?PV^0PQd1(kSF%T!?wZSz`_!S*'
    'HaX_b8U0;ZuVLq2mRC<3H*A`7wsvVhJwmW#MC-3#Yx&lg5O-`jRBQzDfZyRX;=W(fJP+C!^2LtIYk-|7+uAvX2T2<+b7W(*Uh;{t3&{GGk8%ZT=@L69kFJ1M'
    'VM~|hRvtZa*%fW@Uv^FYRhby9jX1=~`j=fNTpe6nU6RU?Z>3GHYo^u$B$iz^ioOc<XAS-#)SjQ){@(dI`QDum>xDhyJF_q4TtqP^MxSZb^If>ZJ9ioHkVG*s'
    'ZMb~zhl!zM`ZpW%KbVd2m=J<!DB%n4n@PcDZJe3QIKCIQ<BPm4PgSg<xNs!p@?=4euY04bOlgP8Y+BgigcKi5goY_5FhpK0YRD}x5(I33lJN>*uF)56ySM^j'
    '#f@stQ99C9Q_vFHTjtjoK2Sz2)Q-y?ktDJnX}Zh)u8lY@+ZhVbvUsYwnoB*;%h%UxxS-`5pkq9-<X?v~!?0^}*K81&S3Iwed9tLI*de;&^n)`l@9{V*cx>aJ'
    'VW3}ujFj`5>$Zz?qS{8j7>-og{q$`#K+GL<;8OE~-d%gqJ7ks6j~7FBfx_^me%kAQK$UrKh9w7Al6J3jjnA$a*wyS3tABC1lo7o2<gcCGc)8>u%`YJ=E8cOe'
    'fu!3aNN&xVmy3|pRFCXDxCODwM0y%89T9!_c%|V`C*d}1n~o8Se?vD0R<yhhnLv=2%gc*YG|Nz9t9R+r^1c*xs^;&MH%MpM1_A0o93&Rs?%YwhJ~fjQT-Z~y'
    's^ubfUc4J&kb*>^6iIldjO&o|=Sg^@>}+9cwY?f)P0^7vfz$pG_bT)2!n5K(Fr~GSsRZ%%Ca#lDv6k|#B2B@fb0;@@g8^L%@sb7$Su&$zP=fEoqUzjAK^J7+'
    'G^@n(5h8jedIy^GB~`G&hMa9}IRB81iLU$p1a8`4;f1fgc2Jzc(bDEu(Lwx#B7{O$zxkl#`oAA$O+kazSM)$y7PVa`517lV$s$7sn8|Foxb<pd{({a3{b~fA'
    '=5c;WsF=(a*`TJ+53w2eGA=Tni|U~(=Z0${lo9s@?TT=8DpvGOTCSYC-rg<fo`BB|CkXv~r}-%6p}a9bCpf-0IOf(GWY%*^EsYS&nH;r~YuRUO(A@ydg(WEn'
    '5mQFVTnSI%Ly-rqyV5WfSXgSaHfH?gj6Pl%t1<dmvOSU8HTN0tA%({M$<0`Q2!FfZc}@Yw{l<2C;$UYDheiK|-)JgtDKk2HDc_9YH~hPhJSgRlcoi<u5EYXd'
    'aWZHzhK*ehvjYq4igqZZM^|Hvs3sdTeyY?CpO=D9l?AByXJEAu74r4eo;2u`#f~&m^TJ1y3WM$_xW2qgukDU&`RZb8mBJtyGnD^yVuRNRlA&T`R9<iPy`3}u'
    '=*{E`5lgSL+1Y4v6D=m=A+jiUOKC90CjPvf2G6=D&nWS9lM@cWZy+yLx`AiHkexWuAu0r8hyI@u4RD}{4(oWBM3^@!wqiz9BnG~N|KH|p0?+O}pTRRPKfyC6'
    'Kf!soKN*d({=&^ua84Oi{AW)7fO98J!8y5ySlI;f*#piC0wCbU--!dvTrjc%gXGv)_ZI%}C!jU0sEssbGL1W&rFonKx)(%y=zI22aDgRhCnlSnoN=D}zcP;f'
    'SIUQQ@9_8~d8Cu5W@UcYc*$!4<e&dv1(5%26@dI_|Dyo%QSq6_Mwb2M=yLK<`jj-%HdOriX!y(Xi#VR$MR`VSOG#<I5v$!`-jUo2sOh<TCX#~4Al!&w5%u@k'
    'Uk~;7+1Ez>eO4OZp)q_veZFhxhUS0@5uctF1#bKoLg0QqjN89aX+x;A8sf`!HBoS-lX(GPX}e{Cla^n#!RS#ef|I}(sW!)97Ih9>_Y*Q!R*x>VQ(%_My<VqQ'
    '1Dkc?K#hpCdjBM{n9^D#Y^@^=4sPU;5EZGkO=%`gw5UgdhMeV=f!8n+D~EV%!bx{`$#0jM%abCiX<rB-{rJvw>6>-XM{n<d7%RK57-i2wqRWdMJ|3M{KcQ*D'
    'r~H`;f=cp^BH{z?rM^%$ElyNX2+bLuj59iOr<2LZfiTseqI6WPMhUY&)M9=Iq1cZB>)w)c+H01FPbcFmnR3nvF$g2tY3)Z!86>FoI_}Qg{OFR(IqP;kXj;-+'
    '=V8Y6i70>*R{UImEQA>{-Oul($^AUExm5`@yjJi}fpN&)LV@mv))wc{p4j!mkPriEsNJP-kk`xdX3%STiAguem1SNF%)D2jRh^{s(4WGtQT^C}J@HsLqi2Ut'
    'g9!?r87v-06H}z^5088mG+eJOS9`R4cPVf?N5K^8CFz=wA5rVLV%55Q-LKJ~B?G8OfBMX*frM(yY3fMKs(S99G|at{uc-tLN-G$96eM|DyC(Ci-WpD0dTact'
    '=whK5uod9N0(Nq9Nz;fNkb6DI0+f42xcEy&Ds9*`^1@cmtp$Xz#ErGs>+W8G(9}i>n30t48IMt!idCqgGmIi=v=y8i%RxMs+T4o9vn-k*AINZdXGh#6(F?^O'
    'aC#0eiyUr>4!!KVdQq=^%2Eanw}d48PXdT@Cgtt`anJq|rZ2pDkB^RCYJ51vjYM)7y_-x1bCZHEi^$-`K8NZyx?4(btbR6`T>NPUu#;nh>Gp_!KRf#EnDE%P'
    'nn|>^1^;Zv{6;*L?iZ}ha~$QCEQ8g2*2PVuj8gEE#UTANY-7UD{<bmkvVApmrLO#|sVhr#d`7>gH%y3A)-Q9qJqKArp>gN~pw)LN>hB`5w=GtU$}iCGt)YCq'
    'e}x}1aiqNpuy1x{OOXJuqBy=!-CBvGCXrTZKOfC<9XnFh<b6mGyE}?GaS^Q|q?h~hCc2v^ku@##02l}vnSukmgWIXq)`sKpKJk3rZR2FAD%ZA87U*s*#jBRi'
    '8_Tt;xHmVA1=C+`!XFEW^PV{~lqfSCb#;!(ddoLviGtwX463W>YdugAPB?+9kg)MBj*EgwQ5PekcwU{wdKygKz)pFrjOY#C_xgCJP&2eDoEtl^zhn*@fi3JS'
    '68)RcXqb!Yb$4uuMl~*OKBRgm?un=C*4dV3T?$u2pVUfOcbnmk(82v#pw)Fx1UiGh4GV$vs$N(vp;A46^6PK1e7N~wsV#5yJ1(e9e3K_0ch43ZnC%v}T~JW}'
    '$Zw=nmrV;4+fZ|u49B++`}?Ff?e&KX)Y>;2qP(@1%lX)0oX8I>pw+dBpza@Ocrj*4v(aw;Vq4X_8iye1bw3Gv%}lPXt94SDmPXJzDR>{`G%S*P*XNV-JQi8m'
    'zRcgGRhWyXf0vv>Zhqc^8gM4tI<rz(DN2XHs!biL(kiXh@atXQrrIaJt$f}U9h`27UB2}klPAb&(0qf9FN57Jf&W1Em#VOnL0F13Q`O^ev>o-`gm4smtzs3Z'
    'tvL3EzKPEIc90FKQUuq~yY8uSr#74*s-;zKWeM~>pl;H+39#x!*AN#tuovpnR??#p@JW%A%gV~Lz$l8XDmmrp`cQ3NvJVF%B&TCDdik7MOfRylF~c1xZ~RoQ'
    'Mv5~EfzYY;3iAEVDu1c@&U&_-R&2RK%<asb6=J%Y|Exmn+2Qe1oh{+rWCFM453pNq;NNgB!adVJpTH4~K*mL-7+x#YxfGmU%}^VXkqRrI7%SC^ooBPbpO-7)'
    '+0!jfIRvY;yCo0a9AU1+hYk68eDLNuK51@l%afPSUv+;uAU)c{20=H|;}=Iqzy5Ua1T!tDl1H!M+gGGSt3Ek;TTP-Wd5GikQ33SeK=QZwNcHBoH^0fF1}Sy$'
    ';mPa6C&(#?kFfGg|5WKu2&jI$fvf}hD!{KD3J_su1o(-LRa3GVZ4o*yDZZ_&2lK@Y9$d{beD>rBc>B-d-z|Rbx|toPnMZCjTe_KTw;81YblL%40>^2ZQjYVw'
    'u?J3L58cMLbz?hjV@l0f*w|+^rO%FDci;T}n!WL*6Ze?W;a>AN+<W$hRdY6cS&{~Oy6q?hI#ovNdp_9e4zfP5>=TS)s$ezvj9{GguUU38gWE?bgYgktZY&*f'
    'J~IOrquan%Bva)<O)_-_1h-p?Rf1ljuf6a$6uqP)g)m*EI;DzNC`!>_r)O~YUQvz)lwiu!GjIpsc6qpo`MOq1#GsVT_^mhUvnxC;GU6_rE%bw;kz1h&haab;'
    'BZP}^G3!M%QxSiH5eMiCdVzKlm~5Dj3w$~2-SC7&N+2^K3DO-@sN_cBcHg)b`xB_NEzXq1a7|$?Ug6jq^Slot-qk3pvBMZ)l86TwCBp1tjD<D)-$>`x8%szO'
    '1zDUA=h5PJn#nq0R-ti}_4?=JX7)JM^<ctJoG$c?h<bAvbT*I;JMZ^KoQ6o>39%Kp0duZ*4qOCnZoM!>VPJ$r6v|cm_UO=;0cvdvc||w#?S=>YUmI|0ZS_gr'
    '`y~2K9%!;0L|De;4g-pRyke<kkl>*qjDStd^;zRurexNva|DH+hLVg8Od)EMDU0<Vl8C}-<_l}VUiN11FiMy3Y9^S<03(Z4KpQ;xgFpYHg)GK!M(Dh=>^d7?'
    '5kk$?oVXj3M#Ok4$Dc~iuclL4(W^PHdu?(xgR=qBF*+6SkrGX5U2x%pZ_8Gjdnl_-J3N(%SJ$4r<6(6tXGB!-x@jp^K@s#8U+Kym*HYK+X9j1Kv^2fjKp>Fq'
    'q`V}QNZSbLrDCOX`7N?rFT+K4yH<`1EN-$~h`h2!T8r$~B)0HXd{l2(+o+OWWVgYz7vGu{=IsHU%w~~<nr1VTBvzLLQIX~$<_2rZT7sj*@46JJkg%D^MWV0*'
    'vi#&UlFG(W69=qnq)kSGk(0yJJ+zjSFHiuz4@<mMfCyaCN(aa=e3_Ja=EA>G(;!~FaY@DiEho!Nx6N#Jm?(wbcvMO<yNgu{r(F6ZR<}5(k5rHN!@R>G8VRtl'
    'HC&yfft?VSwPIT<TqBAX3`BlL=b{?&+S95{f9EV+9GUv1YoKSBjF{ex)3fkge;d6P5pu4j%cwV+Wxc^I;fBF^Jwq>LzJ1|t*o%6w(=XtDt<Q(>pWaN!?d)pI'
    'b<B}B!-_WV>Ks5H*miAcDCMj(@>B37NbS<t+%44K=IAR;=)>KI{v_TjETJlH{0s87Zr8<Nb>D4NmLbpsj#27xY{BG0&YQJFlZG|e+BE!ar<xYqrS+2G23Mgv'
    'U6(UbmQAV!t()-@#Ned|V_^b8*CJ3~a#%`S{A5e6fU~6=()nq;4(R9MP5|FC@2bKHpS`Yi!MOuT0`<zN%x-*cHaO>s>sy5qVfGIi3?`ZXpr|=WXlR31AQtO_'
    'S8z4_a^4l62H8}PU`)7|Szwf+r$Eg_y28`ET+n0&S+NQrZh2pq2yBXjW?d3;%nCLMIF<9-&2Vwvg;{YJBC?iq&Mol+EKJa4tRIPDmTA!vBMk>+5xrEdq`@}l'
    'j1f#xC2!BEcCn~Y-1s(HI;bN0k#oU^F%Zg|nduF8>b{qz^51Qw?jH8Gxx1n5mwu!PP780h;#_2l8c=6k?(sEpGQnJAaD3G|1<tSXzA$w`IlEgS?-P#%vgA<|'
    '-b^CTmkz=hKzWyJq+D?!yb?G2xG<)}TCQf!FVEYPYTwg-Q180v6M~0;0{dc3b-MWtO~ufKS0N<a7*Fw<`2-icZZ`rC@C4S1_fx%OKNYMS9VDv}SD~ZlS30R='
    'byB5vknB0LVk^6{{&0}lNEEgRttGi)*Djgkt6Lv+yv%dH=suUbT%^{H<Cuv}<a{v|c163w0~wIX#`s;AqFSghMq>pqSny&9hznW_0b=CEVKV>>|5zO^h?MY!'
    'LY&1(y4gl8y=vQ4s^X+n<{yUBR(}Gw4eh&mB|Nkb%aNpUDP#^mbdevIyYB-6-N=n~&A{)|Max#zB=Uh#*5F>Cil-9ODjEyQ6hP6%wjo6+0CGbW+^kAc*?d2N'
    'Tcq;cy!G9n5`72fFo{INFcJNNfW|=|bx4Z3r3F?O24gqtKnYA*IJ)+PJzN|!kLOdx=CG8C=k~M>s$8(k-t~rK`5a4k$U$(T;*lpGy5!U1lz1$vBQ{!nPa~mk'
    '667Xgo1H-7fD)}yHBl9sYShuJ6dRtY-<zLn9szfxkOS!dtsSU}>C&*{sw>)BMn_zA8h=oYNERBX{QaPBYwFoX^q|plgYz#YgN&9LJG%0||8D;O$xgt}Bn7if'
    'glj-wQqhMjn@UxT4&YEyu}>6|Qs}!xnDH<Q)P4AJ1!dn772FcQ9?>eO5}pIG6Z`K*{cGnRC(J)y^R`%ZC(Se9yJediFR5n3n4VhER>PQ|&}itIps;j9M<ukP'
    'M-5A~(9&woz2i%TQDvcZ@A9#WA#LPN&j;ZQIyWFBR9;~EX0wsdypbZ-zTM+MjyUQDZMo1(@;E_O8$-Z#V>!1xSfhGsKKb5h)$_#g4~{n0`F<P5S-EI#wbQap'
    'uJ|mUh&QC|&g?U<-$t~Bu%l!0FUWec(J-4Sj7qZCh$;wou>zUbzM2X_3j<f9+S8NzgXr6balmzG`6{AcQo(i!x>xaRU&1sS<T*C$vk{(c@5)O4pwaluzT>jo'
    'd6zGC`t-YSQs6~rcR(Mzr7Z;AkL;?*d($xk7{@qU%(feez1_mcG<g1A9K6bnMl}x;Cc@~=1e%`Rud_M<A@xBxPN;fUEiVl+=!bDo?|2pn+<I8lA3#pM_K{QF'
    '8Z;4V*-Igua|yrgv_HD3e6cYzea~M!?GmTywXb^5jZm~W7glZ*Uw-(p3CrtP^^1<aI4CES;r@wodZr>}#5Lb*sWl-ws27%=Znb=}x%waibIBbI90kI3Wr&GN'
    'M|)4=awY`^w%qP7nJ&|GZi>kIw{%(gV{uTtw+W(d)1gQmqyg$A4L(-k?{lf3#KHdm&(CVH=?Pc56+k_R?id(ghYaH=spOJ*ahy{8uL5zrYF$*kMLvR8mC!M~'
    '6wGGz%nb%`qwnl+{}r;mI{UBK+c5wlKrCe52xjXHSItzkPSCxtm}Jis@$R)I$%)p=XZelU*#Z0K`QdPdkAoqJ#T?{Hoa9=L!iIHo*bXH$-Lup1ezDJRaST3B'
    'CUvK?UWNd*YK@ZfS5HGD&7D8X+lx-0^-YO)uOrG)#K`QT<~fwCrSw5z(em}j-NJMq)z?D)^wrQ>`zl}CDsRcpZXwIIP6gqQR(=(PQn#6YcNj&>qxs<*4V7x5'
    '`}gX_De^8wvh5qCo}M6R4@*m&GcNhp3v@QMuN~>U4&LIb7>*0A9w<d-yaO1cuCxG+kwNCsuA{Z9Ee6CxfEnCNEow4ZF@c<3&K6}{kv%0XXz0hrddQE~`B&~Z'
    'w&o^9|4~*D>OU3dk~a9aePgGM)kfn|8dVcJm8Ok&B~Zy?1V~Il2`?p1ea^PHz$(h~HWcoto46nx$uj1}E8|+O7RM&+2vZk7n8Tx|<~TXIm56>|PaIW#s4io$'
    '@Nw+CD$9DM4|{(yz1<uDWx+qfAtAnUucX<s@Q|Fs`mO;YrlS9Fwt%CzCvOj4s~8cE4N;LI93$cehmhkamD2$tcS;*Dxk2?zL5N6noLycGXW3jLSbC?E>+EYJ'
    '6FAXvBRf0%o5DsoiUfYSQ6umm5Htc$?En#yYpY4jZ^&)=__r76HD4W1E{3BIRjKKoa|oPxIRs9e90K#4Z$3OSuKDo8^UQ}Qr?bh2Y;1lT;vUExFn3Z7%!~2}'
    '%>TxCvF2hv?cG?qr6h6!wEtYd{pA4RrNH1z0l|xaz-3zR4*Ts+DT;rt_2vWXj?}FF2Qw(#V@`vNT!?~c3k<3vky@CE>9GIdYC4zLfw`40&lYTQNf9z~y=ktM'
    '24Vg`I}HM&m!weu;lDIn!pSPx5>D31mf$2w_>bpCurNPe9djs*oA#ug3xPplf@mIjXbY<;8v_F$Hx=sW+fci52E2xs;axzh61#MV{u!n23f-fVSw1c2#1XOH'
    '?Td0l6lR^E7IL8yeujpUn@g(hp92Gl8Re1u3AwRSa|#@=K?CB^ySE9x648mO@sBh$v3wuVx0HMnU*?R%Tn(vAd<%}Hb@K}EJ7whpGY%u-OY^D1dtJ%KvIF%`'
    '8nc}x;q>YjQLIPo9!ikPc~2`cmaPWY<+!(!##Y}so>%PURc`=0V4(<Y<<(n#X<=d_T>#hel3KrHJI^Z$OFE%wq!Tpr5V)zVo2tLlZZ$ilJWXy#@Km=#*0Z&>'
    'Z0xjAWOA~G2E!qEWTcGLQ3gUjsi1zgR(VS=Ke{iS<3#9SJf){si>^*j%N>Otyf}LDD}tTlvf9gy|LBgu@SRD|JO5L(kC$2<f8^Q@P#SByqODy8WSo+)R>OVO'
    '?_W(Rpah{h$Z0R@PcER92>s5;p%vp5S=&p%4mtPP$&C2Z#VM@mDYG*CH!SceJD=gvpmTnTGlR=c8qHIf-bFZ50o7YRBJb=|lZ+oWnYHUp|2BuYZ>v+<(cSI%'
    '`-~%OWJtgm4dI_l8I}4;WQ<QZ@fW1(8uFN?-k21U4p$pi&$y#8&7|rxcQ`y0MPfRtpF9@#9i4skKA-4WN;7rpPy(}|J0&`9Z!EOisXgzye@SUYKQ3yQrBkN5'
    'M6@`&b!qh_=3^KaPZe!tsf}|S_D1uG%+(wy5o#NzKm<|oVD@!1pN@tLM-ajBsKh}hUo&yg$zM)Ct#k<Ysh(DK7HFr-Rnl}zj@MIASG3wf)#zxbJ?-_K71mn6'
    'qV(04iiLF4q+d~g*~)6IS&<*yg%wrSqGyp$*V9zri<)>Hl+!zUAl?r`>9>(6teLw+)#N;<R}R_k0(L)}U0%ulw+@H$AF>CoVHb2{9!ur0Usi9qT`=fdqwRy<'
    'j&&mg2;op^ZY^JbQr`MJ{QX8Wpzx-F*BI&RapXg6Qs9>WqJ43C<$TrM$%h;$z0Or(DVzh#@+}-{IHR-vxl+b&HMSl$cAMKj93P(i_TtUS=Ea~zFksQnBk~}e'
    '8&Ar~cyt?0d&2>7fC!+Gy?aMp3blkGTEdq`sP$&_5PDkMXeL_^cA|?6>Y&DUxvh9ls<yruB3C<KYzFiplP(oY+4~d3rMdDw(-=QV4s<8+QFEBG%r)W*u3R{2'
    'gQw4j{lE(SBJja)qvnoGqT-qDk&(BTetz3S43))XmbD_BpT;)LPr;eh`#?<sR%W9QX{)0e(pruj;rgv97Ko+91xQ+9DludN&!m!Aq@@C{yKp#A_#SRMMh=dZ'
    'fy!rBqs(#l&k-~)Bx$|&KNKe&vEpl-HVb2FlE^o$=E7<S_rnURF}A1p^U}$=r|24ozFLtsrY{A7HlY~w8x>fCBMV=OcHj(t@L05^c0h_7I-?DD9619YaokLi'
    'qLcMCw)G%y9){Jy2IAtNN36vX%1dG&&8?mA1&B<piik->0x9~qbjO!O$$VL=nPtf9rB~((q3c}U3kh0r3QC=PS4>G$I;-OeE=eI3SyFvz)wyV-pyLBgskKuy'
    '^@K+v?)coNY-;mS*rE1*f!_m$88qn`LrW5QhMFKUg=?*`Iup>FlR<`|Y~3W%F{|~xB+?-wh8RL(OG8~pkO(Q9AxC4>DkKIpgn-XItsM0^^|en3MO3muoxE?B'
    '+ka=}J$)a?#NKd)ccMRCS~pZYU-xL}2~L;}M=)nfZ)`IBv^w#B!9<Eu?ymD#XpqWpORfJ~XIrXBggZ@gILd-;oyyFaSkh<w7h5nP*ahS`&?{YAzE6L8F0pS_'
    '{<QPn>>BQ1!ogE2Q?}yK6@&@3Kp?z`dL$U$f<TENi6kSQ+lU-88=_cf1#<yA5wq5w$%V=OH(Xj`pIZGQ`eJ2~IeK3wKxcWNPN8RJL9FcRAv;B(JL8pDtdcLv'
    'gKq8+YGd+g295gnA1YIlpK{Hp882aFAaG`d0GjnhiLacsvLueCB%Wr)TVVD0n&ojedio1PZC315N$AZQAvgtR$t243zFBfdeE|l)r?t3qQp%IHJgnKv`tYBx'
    'w;sW!9Q3B-T?!|?74=6T&)47e5Hoq+8zGczR?jY|<E*j7M3VKz@FIf?q@P6@VgVaR=%d;2-EiC+MHd;u&kpAo=oNi%egXCUgu%wq(Z91<b*|{mX7mEvUO=6v'
    'csynq+V<vAO{s624<5v*I=jKz35945Gn)0U2&hd*$4{?LN5g(ZZma^oNPY$rub5oNrwD+GH$6FgW7YJUl4O#Ze=~Y}j&~G($-s=mx#+A2O<HvT@pG}cB>KnB'
    'HVo@{`=R*M*6}fQI@6Ss(H&_T&nL6tzv0QFJ#urfn}Hu=)0WEk+vE9GBQQO`&R`R;zpg*b8{l1VOvu^*;h0c&2^jQ-Mt1{49*TU8{0?wMHJM4ZgTIY*Acg=6'
    'N2l5C1TRX&9`3^}f5qEl5B1-SN8H1dQoMoo=n=KaSIulP&wx+RBgQ5uhr3!0UIn^};fI<h*=Go_IYEOAnb)xnRLcoY!aEo{?85Fb@aAH1PQ`-F&z>C}KmXU!'
    'tL~E*N3RakNB-l(lP3o+4&EF-O)<8`efRSD@$u2I_2T)P!<Q#%t;)b2)uhUp9`J{O^MD@&<N^OZ{N)$?_58)J@E-&-ri=<y6DrzI(oa>^G*??SDNOhw)i|jd'
    'EkC}LI&^con5CcgD{(pnMUDC#OHy|<)V}^-)wL&JNq1;67~M?)@W+B`R^YK?g9ujwrCiv4>Xr1obb=`$fM*d+@98J~n+ak{BpXjomq;6DXGt3gJ(A7kK13T#'
    '7yr^v42?67j5(T{gKhE)w0Uv}ylL8<Z9nYtxzDu6HhrgA<8F3&)f<sfc%HC7gW|Q}z$A1uQhM9wx1EH4HS6-*^(jX-<7V8h66;^>#E&^`lKm`AsaE~l6kx%^'
    'Dxn^@ou?UebjHA5FETsabe`Jga;gVf+T$*#zIR5IpI0q_Gv!dOhiwnZfmec-;T?!RRV_oWFvoenNT;Uw@xzu|HC~^MI5*keSLqH*jlled-vl6cH9!40-Q0cP'
    'PBju&R?|6I9N>CORiuX)sK47u(}o9#Ea?k!c^wo;(>%2(54*rX$t0Ho(oXh8-?b1OpQ64~1&>cL)Qxz<q(Y#QahiI$98`a|0v*;F#SCdJX{s4Q**9~C2e^2b'
    'Vpa&?e0H~6q}hO*FdJL<FEWAQyB1lY>*3^z0i4YZN(lww=7g&qzU7;(Ke@P=Z~%>R21RoTvs4pI{6Jj5kXwfPJ%f7+*ay5TM_F(1gUvMD49A1XO;mfptVyi('
    '6LYVgv&m>QK|Don6K+ZRpk)nDv2&6q0OTNPm3r1YhqkeQS91gKkHb!B3TY9l_`4eK;eWc!m-=tzan&q5KD9lntWp|MPL`8gnM{C6o@U@vI9O}Y6#U|w6x&o^'
    'Z#0!(mu$y;<G}W~w2V2TDi9>i5g}#6a$L3Zm@tFn1^=jaR3?_2aq6A&dNYyk;fd9KC;z8UAp|gM0(su0cS+j^?J;N$k5d=9Dov{>pH*EnFz*y%7uxD&CvDnM'
    'Y-uott?k@TMW@^JkyF*DoT3ls0P}YO;ngtka_n8o&0p=OjmT<%4zJ3_H@83DPn)egP7&X-0&y>p!FB40`MrUQWLM>MgKB_Y1S%)^VpcTNaxP~KhMbm!={-*U'
    'AiXNRuXZ|Z-)mS&iR0TE>l^e^=av~(F->W{v>Jo^lG{eHtuxI?%DBibP7$3<(#Qzi5?UlwQbAr1i1;LwV~2W&*k-p;jR+0WI8sld3oCjop%{g<ic8ro*RWCq'
    'lC=e?xWzs?J*Hb{S2GN!HS|jnHzY1h%$-%ki84zQ3JHS)snV3<&y5GD3eB(aN_A~KaO*;aeyk{t(XP8B$iC3#<K7eqgG1+B#M>~Xa_S{UxRjzMnt(CaEU?-('
    'U5gVTY)%11-(qG~QubrCTfj3^Wq0hV>;A=CEx|LN7AYImTo|UB!X8Bt)6$_R)^%WA1AFJGB_XgnklrQABdscOKvkb^Sl9E%l+{J#zZ3hrE&DXjdmyE!MP=hX'
    '=Z&I`>A4GkBx{rxCG3G(EEB3&Mz{IQqSP6Eqq?0!MpgzuZrTBqop4{NQfDtM>t~U-c(JoMaS*AA1aSSpmtOUIr5oFm8Va_9?*Wc@qn;D^ek#m8SDf<#_bS&j'
    '_=!Jg0aanSpw;dqde^lYNp%DSc2sQz)D#IbTrKhoci1a>^x5k*Oat6Twg{}ew!f+n?1^POKPmoaPsu|v+D_WA$vbHwA4L~KtSdsrV+$!ZF{?Ki8O8XBDt$^O'
    's0@6gpm;YY9DGs9WdoxGqk?q<PAqPrhyf4VYdDQ+J%ZEF*BR~Ccn|*DL&H%duerjJ=sTg@4W{(Q+voJws7FQ12wjGfgWm0CU|oDXp*--}5;5A=3TQn5(0c?C'
    'h1bYfda|>;3fX;VRe0ZZ(vY%?B2{{)^BUvcQsZ%*e?U`lyx-V-z`||d>&I>j0t?_i3>c2BjSCD9?lRsQ&__Jp%ev!JHDC80sGoN+$OLKA*~jBSZ#GEXOzsvv'
    '00Qi0Y9~_iA-M+0_nHHT5^^tW*Qyi)cryHVR!y3XIH^_Xti8@=PkXo31o#1XWG9BlVpQ&;_wglNvPT363tzl}FR7MJj$ToRX+5@@5BKTt?LXXoDC&n56gVY|'
    'V9^b4rfhnt7k0luv1;|DTuNWk9Yda|H+!YKS+~9yT75&-0t3s@F1Mjjg$_Bjs=U)yRGeSo&1m0LPK@MM^TB@Mg^1gtrRy$XGQXhfq8hN3@x{DAyz1DLa*pmq'
    'SPtp*p7mH=kDb(jH>h&XG<o3ncN%5rq6Iq8TP$WZd+1438|<pccg8{Uo@d%i?b_vST4va*R4PB?^>#HQE8x2s!rF^m#`h*!TB7*~rY!1RPlkvEaRZ&6!Oc19'
    '!F_p-q8Q3Ei#c3j+MGA<on?z#g8GGtSj<CKy@W3F2ah(XBd8c}ZvB|E!{9UGj!r~bj}Jsy&!92P?BnAz^qrUon0?AlC=i}$_w|c|SFa9_yTG$ng;LResCHNs'
    'kn6MU$OWB*e{v<7OGM2b>YG#B^G4~z*`ub4o;TG_^1bbIBU)-NI*ZfzI4Ybz#e7REc~wn6e%xfgH5T1*Y;US9uBhE7B@F+dX7Pcg5<O+nD*ZHN2%CiBR;9c+'
    'w^OLmV;MJ)1dQ4c*=(9L?2MI+7u|QUqE*)gELv4#W%z@+3@M?)Ba<hrc#`f11Z{VXdzhz^d}{Pzui0B7k)FdnnP`DfXx|S%Z0*36OE;`@2<-~oZHNb>iw7gH'
    '6D=4?)xvjMJKv;R+pR!Y;r;F|i5Wu;L_aXIx!o3rx&#vS)o76hf#vqt;yXw!z38{madt7eMuvBmvC9zrad}0qbp0MeA<!}s(aFX@K2WjUTTCv7{iu(oT{6CJ'
    'n%bayQ#9LO!J>~u(*zv_+GVOngdWMQNXmDPol=wwtKAIdlcbHOhQHwe{Lp%L(;TJY35oY6Li^GZ8WM;AP21{2V@6B9H_ybH)!9QccWQ@SE<JK_D+m_Q$6bL-'
    '|BWUW;f#mql$PeP15k;D&F;Ite?iZ`+tdej-=kW|ldnpieAS>QpUPe2JLLt!KC75ns2aN@!o0=B#<xT?+*fpOaV#j72pxUz3)w;4#e}|zTevF9oJa%AgHK|S'
    'mgiWd*N*5d7SME(rzuqj+eTBtjb>S2^(PGw_2i|p-RgJER!1L8*EQF^N`XaHM61iUc~=}kka@v{#-DytE^Lx~`ni7Qkc{t<p@_g|oee)C@&-&39vYCuVaF|Q'
    'HCfcEM7;<>`$=2O{2iT*_@@aRZ80SXyMoLb5_?hlN7<0Hy*MR9U{invp~q;(qGIn8RT*$57nqLaeZ5Jqaq;Qz=@cpj7U||3AqJ*8d+T}c8pQW(I?5L0Gb0_{'
    '%;kU2=b2Lu3;LsaZR>kzOuQf88=}<I(*+bM_GflDQ3hhUYFx?4)^rsa!$L+d+_}x29W56=2weu8cO(rMmYjSzwpnQ&Ki(yI7(sl<xe>$n+Epv>iFOj{ByF}u'
    '=m(Z(sMHqf)*9xfWp)+Pz&Fc`D_o-EU)Z*lq~OA~i!8mcajH_J3KXwlW@N={TdL~Lc7N=iUJWQG3GA4XNpyMU0{(h$JbZV)NVR2jYuiR*Ol!5B1ho|p=-)fZ'
    '1N!?x3>(nge;lyMH-e&Vaq|5|Z(5^Q3BOWq9oF1n+bydmYONDYedTSN{LMJA4PXccR&C|ry(|z$D~xm6GPmGnA4nW9#&P1HF-~Lc$2|uAIW<ntgs<kHtHqBs'
    'vKlkxlR01T{~k^)STViY3K2|WQVMHVuwOKoBk)`a2I3M=v#W^{y)b+_s+nN3%0Ag+ikgfju(<TqAR7&l17qiD%}~?Q#5x!4Yyt9I$|J@JsB=BM^@R@F`PC%;'
    'nLdlyL52Q)3|x2}C(rBO=5=obY+o&o!(8-ykrrG;s%DiRkB&yFfTr1pD&_R`XS^O~w2Ler56CHhX1G3IpIT3`4}~X@|5J7tr*QjD=CE_xVM?jT0d&P>&85<g'
    'z3ikN@2<S~s_}S_K9tYb+5^Zl;#b~^@8f1rw}I&uo6k3zSb~v}hRLN09M?hD>buLw*cC01iX=<rO;7b#q1jd1Ada!>k{$$jD7MBnlTgq7jpH&?>Q?5ey1WLg'
    'dMqtSVINpd)t)!W${jCuT)i}RF`|hmXX{<oRJnbjp>0o@z>JdTYZ%x}?EwqhXJ40XmPaY*idf^ckpvey|6GCSdyfT%CsY${fV19c<b0;|X(3aZ>|SxMB4wYu'
    'p?xzh-Wyy%f~e8vBv0TP3|x`U5-UZRrorw3d915yc3P#IUe5w<eD%>*Cunajsm9D$-Ztae82_8>HVLzj&!C@A;0}2SCl;O;nR8m|Oy`6HeX0XGD*aA$86rUx'
    '>bZlf;O$K^t5|1Ay!{FaTRO?m2{bBlL#oPE<UEp)irmz`ii(_Z^`q;Z9X8&+yTVx(K@&tl(tmF?ldUa~4Mla1&+1#-Xx6P~bh0KhWMt^usCM|z*Y)OuojAIg'
    'T#W|N;Ob%;soVo^&Q&pXlClCJ$a;*~!w1>C4>E3_14}m;$ZtUFgn&A`yQW{;o6(8HgDl86KAIrZ7Xkt@G_~Z9g!R594pLjg(F3P$MQcdg;#;bMWk3QJ8M{ZH'
    'Q4kAT<1w(}^)KCLM<;L6HXjr^Cgkj6W?VCFq(^|mhG{Bm*KvnI9J{|m4Zj_qq&1l1XlpB`M=F+rBMKrXLLgEh6p_R!L@E$~zeRAArw6|yfxuq}$G<#(mDV3}'
    'Z<SpE4MVgHVwOXf3;l>MY3Gsb;#R{LByPLvZ9oeg6v}<KX9ZNG=0II~sFvC{BT<h*M%{f_BBYnY#d&gj9G2YEX5-GHqRoJI*AY5YPF>pOp6E0dZOLix9lN=P'
    '%nMXv%n9b-nH^{3v0Sy+QZ3{CP*|w`OdYuT?rvT0Aj8^Ib^B=}%*B&4oTuJW?r?h)Mwqq(p0ENrBwYWAEqx9bEp|b*eOOVLa=_^^0c>i<=jDgP(tDSS+mw>#'
    '(g+gz#6ucg+=g9O(Ws$(cI9+xEV#UHEo`H$7L8TO)k@1l1)vrCa^vpQQ+VuZR`o=?Xw-OUIOG%N&)T~i_&2?XABT6bApmXv{4?hsdT%&(*gzC>tB)5qwv2=4'
    '?ro^T78l>eOUI!iEAaHnj4q^iO@98r){Uj5#$7OB4h_n4G@+Hv+3rKecXy3!K0{ZT<0DkmEP-#6lb8xxM8v<@5S~gBp1gNolt#O`>avfRd;*PVbg3g!R2}%A'
    'Dcs&!geQxy0AlpDui7A6urZE0qgwpO&d%?&aS%)5?zc8ob9{Jo{Pgg+`wQpZ5u2cTCkc4yM9?J8GU}!FD~z0{*zc5*gwtb7{uy3OfjS}qno%|-1mNIh8Ja*J'
    'StiuGa}r0bbx)#cZ`Qk*8=;t8R&)CLqVK#m=pkhqRgT8=1cB{7v}Cxk92A~g@}lK9Mr3UdUY;mrg=Jg+fbA{%l=Z~5j|gW?tyDE~W*%!AA#>=C<o<Yw7gV`|'
    'yOlES4;{sT(`%QOaT#~?Y7Yw0?OtSwupeEJm}&MJ316u6j{l-p?kZF&m17F+cFn@mY*t5Sl;{WgldLy--{UmVZpWcnN-~uly++D7_=vQB*&r4x&2h$|1hrWP'
    'YkQSZ&(z=0x7frsLI2gB#i7J|8V{o_{_;GsIEk#^SVw0MtHgq|iQ!*z&0k(+SD8tBqbClrRjdb8hs79Jh%9ic<K4y;F{+C78-cxICnp1f6t@{f8vpHClqnF9'
    'vuouw04g_()IIHltiBVdUl(W(!w@a3ZV!UyVf(@mM2@mEHu!mZ9~Xc>;I&2=D;oczC@-sb70^eGLKLYn;e6mE!q^BtmoS(ngupbmhRQ;mQx!)5q7ByTG?xu#'
    ';pSJ5qX&%!G#fzYASrB6xT4EfmG%UD&qE5X)y!r9C`a!;LVrhLuL1RuU~BP87AzC@o~Kf;`HUvhCfWQ1W2`8uOcRT^0Ek%yrfGFlRQ>tz_|5Yd&;NCJT#Z-i'
    'jH6{=-Y3o>R@SdVpc1{Ag02?QD?Ar-<E|-BoBC;RbFjsm_lM<@v--xkq@yg;5?tm>(}CjcFqx{{$*e_yO2b59x^%}7&j&;m`s3uc<}F!_1mjHdUP)iIkV?dh'
    '635r!WD@zt8a7fML^0Ya4e@c*Y(+XMumD`G3}@KwLRv8D4XbB$>DivuZavs8PX-=j9-6&Rg79tRHlzwUTTQFmu89!hf14ebDL5mK7G$R27O(kyfPeFIh{x_D'
    'OtI33yB`gxC?uly1qqodU=WkGad?*srWj1d6U2&PepukV7sG6>oyXp&Qk3~-q{FPwd*l|@o1g#C7h!~;N*1VDUhEOGL5&Mr0PNFXu&ERi*v(XDRD=O`bsw$g'
    'Y{oJnxyD}$?{=3_<3jp|3?^4!;ij}=bc44g4Jp;-JSaLCBJBugK%4Vy0ZZGv8mV2_Zg-3q9hCL2TCRtI5UC~Q>UtK*mgqxgoe(*D_OKDmNa5&1oGyL#umOT|'
    '?6>jfPP8*BdkWQ;m~SxF(2i;dbfk!bp<jrMW=-y5vgnPF#n^1*(Ge2e9_f#C+j+Ub!g=Kn*&joF;$LPY`cbYOD8RzMlaWRymW!#oAwL@zz|bStVs9Q?qrfer'
    '7Ii9VbyUw<REZ#Lnk!};r~;_Na5m5FWkX7rZDLZbBoSsz@+2MXLm~|%YP%wRV+#Cv)#TyoQ%^OAIc$@%cWYKJk{$OgFi5q$Jz!`~0|3Oh>V$j>WvHy@GD>@L'
    'Blk{ah{e~=#la-Ny)Z=Pw{w-c;mbPF=2Dk414p;jiVAh(b}|(=*T^J^YWPM@MJ!=yxuh8#%b%Xp`oS%1*nejImGq?iJk0b=6m6V4@=`8KVURU?k7ADdh}(Pb'
    'wr5Dyy#2o8{&MSwFN4y^7IIndVP_2SkB2Q8uT8h!`}6{5;k}&*9atWCXzCaCf~yKH5(aw{2W!H;ZEHd?8YO<{l|&_s1^K8H{Yn?ZC(Kp9Xa!DA!=se~4XK%{'
    'bZRX2W%Zf?suN7=!)w&h`yY;r?#qg-m26G~MM%}9t30|?q5^!&Kf3x*7=Z+P!^^AVF6=w*l#-389o%{kyB|AATg6V#l@ai|Nq4EGkZi`*1JT=U;)5$rm_Dzu'
    'o?{$`Z!NyAYS0DbX`6Cm%1;d@%GsHr*8Ei^K+@Q|A|VFfQKroNUDxNFlrr|#kP;Ph>u$sNLY=pkcSl{Dbs<J2f1QFrK?}73*ZqT*TC{6_#qetn_r$y|PQjqR'
    'w~7~U2B{Wl0PQL1Q^=%ZDSO-1yqdSllF?pS!FS}0h2^NxI<=|ctvr;?J$z=)n_ieg1So2XW5C`KFK#Jr$ydnAcx|~g`N^<d8!qQ}3!?_Gg4VM2dXN$*)rpSD'
    '1N=}KrZ6A7gy}M}nACtk0mMfV2Wtb2X>>7qkx$SX02`yC1T$8IHR7;A-8-iG)Aok7Q~d?=_wh{7S`c<`E~uW+-<v#nHFCqun<|hE3~UR7Fw!c3B+qd#ey)^w'
    'Il^oH94I?fG0JOTC0x8$t5P-|rSL!YX+cnxdhZ70-{?G>4WgSFUgkjT`A!D`&_F2&)F;#yoedGH^L#>)R@e%N&FIWN;JDG4S`hb*FLeNU^7Ak0rz&QFg3BG9'
    '_UKH2Acl|LW!XG4j|RQlIsB?UN}^^HZ&tAm5i$cBhS2qBdQ0_+3<q^TIeJ@dDSXP4XNQNc;U{~KR4Fqq{6u)n&-C5Nn`8Sk$zWl9X`ZN$F&~9|{RHPjzTIgw'
    '^j8n?Zz;dsXh>6shfkp}YcX5RhDNt+Z8bE&C4A~&Ttc~q0upUKQZ-p2w7(la7X-2wUzTD21OI{f4d^dHyr;iUClmQg`?@4mOnOUy46;6gI}JP!m~nQ)k+n6?'
    'y7q~}jTqoWJpLHtgpru5txunmDq*wBpS@AWe_@kd?6ud_0&Y)~MTg@7qY5Scvv;ah+$gCHVyeLo<v_lBm(~=Xs(weLy5_*7ns>sE4M!iy^3Tb?Y~<C%heP#|'
    'P5qQ$#{UNgfhb(GG1!~`>>ZP~@r2JntP|Z(b~OBfeR-Vfk|38-elm2eQ{E1=>-=W$ncIjtYTOL|)>Uw?{7QJ^`hDfYY5EHD?A1d#rEvr#Rt5VPs@k0VB|UUf'
    '2J6joHax9qk+PSZrp=@o3<rfm`1&;IZJfHK*QyQGhIaUs$edQ_xf>FiXD2lNUy)}JN;Rn)f3Ccw%;iXhJW1%2il}KV4Iq{Pn^s{MaiV$#C-rmUNMl78+q5^I'
    'D=q2#JZ10|4(E}`h<J~pGa8$Xz4PG=rT}M0=V7nXGl{lD-+t(b@_EJ_;PX`Bzj|0<I&C}Qg*k~WisAT05}gD*oF>zB;^Yq@YlQ=qr;+qpzJM@4-+%!=`X0Tj'
    'j1LxPI$(D!1zkAd@ccObo~O!ko>H%DQCfAvq!{zNf|I+E>gK+e3&_;?pwTF-QYkr?)LAR+>qfJ<a=hAB=q(mAbv8?S`{Ll$)2dWagMy7@3;zXoY$I;t)Nds`'
    '`LuB`&axA#ibKD+8X*<531i-$zBdrAZk>aB3_(EW=E-Q3&2mwh_N^3-%!HkuDlgAHOdDJnq?xBIlx28NIbyo>Vo%6}<6^mI`AMpGe3EPj%0!<X3$G8m#6=0L'
    '&q>)D!t8U-AO(KALEw91I?MD6hypa8&C)T<g0kH-H+9-#WFBbxs&k!+$He5;rsucwVINUQ(0dx?M``vQVFWnv8jO4F#Q!*PB#TKpMLfc)d-fL-<(<oQw)j8o'
    '#iV1qS*mlrnBZ}!Lrv^1?SRa^n=Huj65d`efFvfSu6WP<T~DE)(+T+fxRKY1q*&A0Y;plrEhe$Tx)Iij^H!zaL#4<^KYXVdmEcvey=`50=bO|#h5jk19mAn@'
    'HcXfODb{YTDqw*b^BkmvgIdXDi<Q1A2wvTwshwBj+h}W3?~?j-0t*D<@#%aqTwIX=cX}JCeajm?s`2SQ&+wVy&)^KVS<*ng>3#}-?x*&{W+xPR8chG9Q@(f*'
    'tUgIsUN1tx=~;8%(8_&_^Xq-Qth%6+)^0YuGEr2+D+ev|u+J^u5BNOAuUf_C^Tlk~8;P&^M_-%%F~R4eL;uJ*!*e=x-}FPLjH)em39wNjqz%GtfbO;y2w}UJ'
    'g!2|#+#7G6gj$OCt=UAi9J{6#rLi;;yB37VW4L&l{Ntch=%4s-wP<aS?6iP%5LsyHrA`zPX$5FZ$fjfUkLA6Nb;<5c?D_dN+TM(ACa@ec6;B?i9C1;NV~L|5'
    'B1&fm|25ebdBR0vl$2>=`=Hw9Y1=-%1rhOfkzho;73}Q>j3?haQQ}gZ{oX%)aA)cRP82KYts^Cu0;+mbQc>?s`u(dZ#T*!owE<nhak(~T8L1#0X<!r|+z2lY'
    '`WT}U2xCldUVO~^H{@kMzD})cS%5-ZI2P-@9J5cBdAt~pg|1!3VcA2uJB71)3o|fHu}eYDR|3m53x@^KwV$(h<5v#F^6x1W?xYll9>A^Hq+64olHy*7BiF2='
    ';`3lMxX7DY`p3{isIWzk+xVzM(E|miQ31^mA*wOoQEw*vhe(&fS8=PbLX1j=m7qTLR7i5qnv9}v$;@&#yTE&!gZ_z-`j@qiWeyTG_&!Z>+$=NGY;cxxJyAp}'
    'c$&f_O;!fzLXLe<{p+OtI!-IkGchRm(;_ycQUY3ok3H`+!*3HQxsP3xcUF}ZP`jd0GU*Erh$01qQpqWGT){NMBz|M2SvAHp+XyBUEW<8xSgG=igScHy1)OzI'
    '^dNY26=SNXSG@8Pv%(F;2>35OS5=Vd3!lc$@{*#EF1o_iH5Wuxf{cA0F~`9Q!BO8TWvbmW=^fo5UrT`FbdOatA%?@35$5KKY=8L;w8HwS=}*(pBnGCQL&1%V'
    'V5+h*KN?*}T%6#tC};a@GDwYjyNwOBRX;l&z1XNy?X<D9mInBl&VY!*0JUV#y;2Ip^wYZnLn-YRmn+v-wU1S$?#)IgQGe<btlvgEn>x9w1a?WD73A3^;ugbB'
    'B{50%5hx~l1QG@_1`7b=GDeg*^x2EX*-hlc6*521E5J(b1Z@ei$HCKlNG4d1EX%AF5M};`1U&xJl?-K`{dEp4lFd}v3AO2QI55vjwdqATF3YpIBqId&C~u{f'
    'ri%N*5su5|qOS67<{F^yi>qIrX>*<N=@3SmtH(v&#rW2+(;UdRSG<08E?}J~-gR)E_)W;UmSfqqf{8=VP;^6^-I|eszuze^&{9NwIiCLSHrNMNy$;j|S&l^8'
    'V5(x>SLzy_au^W&t%m`jjNrcF&I=wC1s)qDSFq%o1r8#H=Q4GE8~tPF#|U8#hNrBMAgj(~FgzRfISvzUEA%a|HGhmwph3>Avenpnh->^UJi7(z^lPs-j()is'
    'ql5H^-n(~jy?`Y5Lw_>Jewbs44^ZG8zW)JV&xU>2TvxNKzV&FUQJ?ogvZUG&?EnK3&qk9QCZ-gOlBnoKCKx*UN`)ByAf5~fU$UNgnK9TX^`{R9+=4CF8_&-$'
    'VGQP;{Kw8ib_L%~#G@O%uvLyN>L<A)LYoQJCuKzUS7)RrOpG<Tn)NXo%+(wnHM7|TAry}%^~v;y3mD-Ax|W}zN^#m-oX-;;Jn2Fyi8tORb&UWhI>?@0p=qxV'
    '^9W_!gr?FgFBym1jo>c~$y~rek9wyQN}`%+?9xr0XLWmfhhmJd1oV1@pkAbk(xW$b8$z3+AB<qEYBeb0FC0Qe0+#UU?ujQqtD5W-i3(D(k#IlpFFVO0eel!4'
    '$zhtKSDKJzSO(EtdxEwV^7UK=T+mmd?>BdLRQR`8<My|Lz)#sbT>W|4?(7Xy*I9Gl`Z|wJEV*ok9etDNC;p9MUWh1Tmc{qvOotoIpeLu@87(VG#qV={cwf|q'
    '_n|(#58?B_uMaUyUrmtZ;+gmGOnv{(p{`M3xk)v_u>0j8gRsTmgdn&P?LE(k5$^%X55QZ9R&h^nP@};CQa)QG8Qt%ub7mBRw~1DfPoMXQwB?|8tv1?JUkmE<'
    'IsPf>OY@A95<E;pEow#0^EBQwui8^535wf6c)5}Ke4Q!$0q%)h*QeUA)a&jg@n%ltiK$yJgT`9R@vRsU*1|S@XoqQX*|8Q9Dz2xOPGXmf>Ec%6F_^L;ZOlGS'
    'focvHquXfyVMvCaQ;rFq4k>{=hX$jgE8N$cc7?xY2ypWe2tJZy6%sNaYJ4>o`n4Ag*pf570uke<-+uoA?SD8)HyF=vU)Ln=;zmhvd>c;00DB9-c<Zzi>UcV_'
    'lw)JWz(iBaH)($F$W8@LFkcgHa;t1=Rb_#X+@w-%@T6H(9E50|0l~I#UP(XjmHfF3#bQj3);3*V2Z+v)@Q@=PY_og@&<}=+aj#p>5I*P=qu5@3A+5yuDxT24'
    'qE-Zyu-HInVl7T^FTeoO)&HOsWpox!uWr#7&bjpYRAAB|Ol&<#I34MDVwpcl0G8YT0VUmf{_5aG_sP-A*9TADq|T83LRYcEx*d(mauRxkS9>;v2b+f<x`)dq'
    'J3GtzgfDC(^%QuN0FO>Lz#dc9ocBi&an-Oqu@kv3#FNw9F8j8AY5Pj3UWYMvIvmSO8g^}^4_~XgCSsZV+tp^CbV-kY($6t=3zyh_fDDQPzOtB<Vc4GLaZEP1'
    'WLh`gzNVq~9o&`n?>uJ|d#sV-1IS+S>2rV`um;k4-wDI-Pm1jZ6Kn9On|D|Od`T!x?FnV|@HqnYVk4b6=!wh$_z+9HhrFmtY_4NNFWt~M3NJih678#QPv2k8'
    'i#^RC{-v&{2i^6sQmqSN$%g_RXmEP&>3>+=b+aiR*W(FDp>R5Tj9c+5iTc$!NaQ_abr!u38E3#CZyDuTtw8=RCKv*VHI921*&OJ8wuw+Er)ba^F3=#-i_SoL'
    'K9ByO;r;;<Ei+yu?*i+E9|Fl+^v|UsD80ZMC86r|E<71!?2|*vfC+{L4hMu!dJA2p8pypOLQlbL9&g_Jly(2nY<3S{y*d8<iy)1P@pYr+n?`q`Jjwz8FYmpt'
    'u`hKkNn}G`qSuvthozTdS>Eer+>ZXS)!aS#_4#Xp&%r>w`PI93un|x_@@+G2QGtkj=U_)ICa_^9sI$J2%q@f7ZG=7#SRek~+)aS<Sx8CvNRo6!P#?X2#K{zy'
    'E6S7wV3yHlMgE6eDx|u3wDq9A^$51MBz;(%_ZA5!f<bi&RrLWR1=_(Ez<vPnX4O@XTgHm!SF>w)KBvqQ1L-u}vp{BWR2(32Ga<+TOe;CO=3=^2F?8UF4jxw5'
    'M<~uQ2{hD4;o^8c3>JgT)lF}%6W83r#AY-22CJ!A&2>#$t~8Arae_P{&GK+glRpsC;pt>>%hkz<$+vb7>%(arqiPDBZRh;8U6QcF?*D-Pqq+T$F76-%vpm5t'
    'bld_2_qiR@`Gxl$URYOzL4pbEsw`IY!&XAkr;>K|fB$w!sAk=3*pFRF6J*Y{^Vp6&PFQ!GNa6=|v|aT$?gtYLRzcpk(ut!Veu%bq9M%U50`2j}tSzI&zg6@W'
    'sKov&=^*E<f!E)pSf!sVyf-6Q2kZ*DhE|Nzd4+ZMl}_C8Be&(e<=~Gnms=1Rg#5P>c8{?7$nItH3dN#@oY0U*OR1Ob3OSxsf+>IstgunQ3|qk@KNXBRiYlz$'
    'tP}x5sbPi@Su82WsyuYgDhQcF3s43-BXbu3-y!EZ=?g6~lx!6_ih1jfag9U-a-Lq+VQE+NF{u;*&;&TJK>u3H8<HdFG*lYq=6=qHwi1YO%b(%0!^!8FzhRVU'
    'gbLtPf_J*X^O^~Bx>I-QjaI@MoS!Mx9`}ciIcv^n15o@c@(OnSMLa=;9#=F^klx?_$gK0v=O<Bfv)PK?Vs3{Qy?2oy`C;ZZy5efUMel5PZ{Yo?hmNQB+zF5r'
    'p!&BjyjugIdkBS})o{1;r)#s|&&Z-E$UXWYs*cQNvdSL5#!Ksw_3VhA)I0|kLXOeiFt#WHU!em7yMCyg>yfrP@ZQGN4dpY+Crl7IQ$8aP+Wn}(e>{$UY(CPl'
    '#oBKga~VMcl<{am0mg2+BUbrv%A-U_;N<%xnUm;0o%W*RZ0>ehHl*nLT2Uq>d!A&^grGqRBC_|E#c|^xoRzondDLR4d=XI{_>yXmWPJGb>GNk7wi{#OG2UA8'
    'QPAH~x?^EMnIeSjrL57alJ9_RVDgf$fOOk5M`ApzGkcfy`sa8l?18-ZPE6?i-k7W}%)S!yLD-kQ*{um75l+F+U9)F=ZBcLvCuxeTEKQM@rfH9(Jk(9E;yk!v'
    '+UgqaVp(h&HpC^*eV6ichRGCXSM>oA<MSNGxwo}c>>QrG@dP183J)VL3+xtpGi4yp(y|B#sDR5QIiAA>sBjk214X>RxNvg^@pbXh@-;I1AmnO9=&o>ZQR_n8'
    'p;78bR+>g<OVN$+fng)#5G)?%ElAan79Vlj_GSw&8iop`h<Ha$^UX%x#xLO5Q6xE?H!~Z^Pwqt?twzNT(dMepvXFxx0nlJ;@SkS15xHd8x4rQ?={3V{(KInC'
    'j(+a#9k&vHK>UHb2l1KOhU5`|4Lfyy(YO&Xr*O@z*cL`~CJ(n8%CRM}ET>n)(clLXW+T1>qnZ$G0>DG!jN;}wX#qjveER$s%iH~f1vNVy*USb>yq%SpX@%1i'
    '$06`xdmJIK71}EcwQ5ieOnuII-cAb2AK0@mRhT~oz|Fp%<51fq%A|(uLDPFmSh4)$OS@Ajp@^d|fh@hn(8pjGlxrt$IFKybRagp~C~FtWGk-_fu1;o(`IAp_'
    'Xj^oS;r`Mmvc;R4=PCXi*p|FuoL#B#Ai4b@?n^)m8!=&Lr%?j7BWf(ao2^cKPYk+`0aDDTyJKzT25&RyqMWwbg#IY&&6Jaw0RgcY#`RH67|tG%eAY$akFIH`'
    '*ADuWi^3lv41eU|@J9&5ANff95kc`s#aR4N2^haM8$Q=|2S}9MmRt&m5)_TxYW~;%!@hA{B_vr=;@6RhwooQI&U%B}`U!!NouCuf!QdJQ2dX0f-{|KV5Cl};'
    '<Ih^RH@N1^<w-<;pQ+bhL1H?1nirVq;ftfAU*XZV{QUX&=w(C@I`ZJn5&Q(1Le+76^ycu%8%>ndM^vxM0D#Ya;(F~zC%^sl=J?>ro9@%YpWd9fRd7xb0*Q8V'
    '{iqZ_<h2&*gg`n4kaBu+k^o_au4stUtMd-v50$Wuekd6+iD(H_Nh8A1>QFM*|03y4sT@iLILFpc3O!}-w}wue^u9#0uq3p#t)k`3HryA!bU%`v7`%$UX#RsW'
    '4zg2{U1V}CX|ald3haE$b{Xg8Z2MuCzEw6G<()5hk%XL-L*1L4o!Ob7BXcS@T+Hr;;?p<q8#h{A?VLasa<W^O?qJ`3trP1YtmbwRWF7{h(SS5QxEkLiVE4A+'
    'C*62wefmS1WJLMDB<wtm=;%AZ6(jv$hLQd;EI3b&uy{S?wdX*uM8h30`hO!X07xe^H(Y1!M7dBI11?ohr?ZKqV@Y|QX!z0-MO1NK^qeXrKl9X`L^}UwE2({k'
    'Z8Lc6CHr)k-vm^M#Z)?{Z&K4QHzPF`3!V*)&wAHvV;DNAvO<7}=YXF&m?Sw*peUHwwG<yTgkdw6e0eT#cOhU*FoQ)AQY-COX@H$I2o95eJ39%^@RBW^-_F6r'
    '$DAV?*JCOEPxO76u0(dxkR(c&n?7#PT<UR?#9FUjUrmU_3xBp#p()){0P-kO@Z*g=3HxFyc{-VJ7fSM^eHt#<RR#BU!X7KQWj`m8n>j5Cq)v+(Inh;BFT=+M'
    '1DVZ8*dU<cfEopZWaYlgqd3P=-Ps1}xvONMD)v#!lCS@Kh=&fXx3$`&II62?pBj=2kFfRFQ7=djun{{6h3%8R5t;mI*h({)AH++pqUn!CeF9;a3#3G}1}OgU'
    'G?XMDLC+Vw6VQ`6;qtNCH#P|tv~wsO$B0+Ek<yPnX`;?QU2(r?{>|)YgjIZiDHeFq`3KI^*w^g@Q{ibab889sL_jw^mq~maJpT@Tr)fbtEGJ0aF2so|$3NSq'
    '9jWWiVq*B#+lvM|FU7!5NMR<;Vzk>;&0-tOSO2x-(!<v@rea-!xO6dH*icu1%a1E*sT4+hy=#hil|q1VMHg&VS23r^um+b1GnykkohW)*aBj=)LUm8!hzSe-'
    'O9+6tA7Z~0=Jaq-SZl4YS~p7q;u@^l18F@rpgzT;(lAUsc&bA^f_`_jBP;S%RAht3vmwrE#w!tfA{TrR$=KekmKaD@8SAB7uvP(;r)BAGwjC7j2&Zer_;oc;'
    '>+8|HSy7qd?kY<E&sBjrB65NL%ln)*veBLRwK=q{q{bi)b#WB0-<O=2p`fPGz|rN_;A|I_qOC&<QWO~6@`K*nPSqWq=V7^$(7#JoQ4-=o>!0_w8eQ_J?cT+='
    'bJ;g^qH~S7nn~05oK`aT<=50uKHS_oXhm;SgzS%X+~(20ve~5mwg*cVy%=6zq5Cdw#oC+ho5SOm9B%RA@Zk6>XeHk~+&ajsCF!ZFzr(2BE@ezd(n7z4>=>qC'
    '@o=kmSD13EBYz@L`HxM8!I6G=kTUA_;FO)d>2r9^vX$GQLW8svP`aPzBvoMv=^Vzp1Pa=cn_Ih96KWhtk>&!md>j2t&^aTF#2(lG4Vz5h8Yh#%JfEftL11Zx'
    'krfc}PRk91AR$I^b(38ZjD9!`HQ#3_r36re?8X8*r*ESZ1Qb8Ll|*lYY~EKc$2s+nUDqZGr?nO3&rrKRp&eK8K9ZJUzJPBjI#SdYi}MUP`M@N)Y;RGTC1RYM'
    'Zns;_MyJ5Tk?RYHF08k}Wr4No#6{UR?W5eTnq$jk+o>Xuj;YUgiIwZYhI?Gn4iSs$itdUA#`vq;A*+$5Rc;b%oU2_W_kNMQe*XHf`7nBRdpa8qj$mI9C;^@r'
    '0(GEHU?$!{mO5p=!tH@w>ApOAif((=!`^Ik`{cGi%Bt$s@xfbSGHuk+pf#k?X}5MC;vVD=pXht%30#5)KfO5AuN>DwZbe;GpA206bU4krM96`W#ko)$f;}}O'
    'Rju()N((w>N>CS5Z!~J0a(q<19NDM_V+<d(ENN9?SX7lH<QH&O&Q@|#M_{@P0xNp~`H$m`cH5vpCn`;AQ@Lb$i7|D*?V!7STT-Xa+N!F3&`C;L)3r67+AM)H'
    '_g4FU<YQGCNY3pD5ysfU7m_~28s!S)5WWP5gHcAV5g_s3^hO`%6de=Q9wa+4MrC1?23u;P+7><o;)K68ZFGZdnke*6=*_3CR=fHZG0{57w)u0%{P_U>eEs6!'
    'm6^0o@(^FcZa%JdJ_phUV!RfdYML2ru%li7Xn=Wds)CZzPc;um9OXl~jLFkJ!gG@K1{hUFo=hs+Crp3+He1xkS%zvccN*;8ZS7huZc*P{&s_Ty`Gxfy*b9ZR'
    'K4zU7E$(Te;7=1$E?~5gbPAZX3<HZ4K!H-1<BpXT2>!t>!(R&1jyJN?cX)DmAg}ZvPmhmYYY^1XmiYH@DrvQLc9RE>V)bsm;u1GjUgAc6iC@0u8v#RdGt@>#'
    'TR-k>C(+Z3A+R&U=$FyezXy}+7&EoeMkk233^Td(;GVlV&w6;BXje*B1H!hUJd9(FLc2JhWtqKyaNTeMWHm5$jCk$c=B7j9_y}89M&gk?A03Wr(N@|A+c>4Z'
    '?I%1p`AM8y+~B^*FX}yQhvi%1(N40v6(`V<T&knhb_6O-aFwxKbTOP$kf@&R?*`TAJNBquX^NcfV=kdL6rJ*%SNG`b$>gT=CNf;AbrUEkq^8Ya_9r(fSyGl='
    '0F!o0krNHpoe+emqqXNbgIbCBZ0)H(n>JbrW+rCaZofC14G{!oF$8I6ax>=O+SAF^yK|~$kA6?!Ux?9sgBbWgp6$v`Gng|8SClA1a{o*SEh<9SYr%MC-;q&v'
    'wh;SEKidowfGulLb~<Y0V$_pShrir*zAPla{%1Sk1_>@U*IuBDMf7QVrBXY&QgS`YmhsC!@XI^bhKvhsy2vo}TzR>zkQjS<s}aAspEesV&q)3yMDCRMPllJV'
    '<qbJTc*Md?rvW^NfW0Fz7GG>J&Dj-ILcu(mqAZgE8|cJ|Wl2Qs1`6@Ep^T)=t<FZO)O;gVFXMFXHyezEFb`r^XcHMRjjK7MipE_7fhuNQ>zabXl39nfq&!3>'
    'ObYZsmi9G?%JCC9qyvOJBWU>eiAC6n>?*}5CLEYzb}!v`s#cViETw8*PVo>G-R>|3qc|L!Xc_zv{>J}U?7J-;xvsRiw_;g9AUyKnnD8x}VvUJm47wNu+9mw<'
    'M((lj1QaD)nlf2fw?S8UH(jAH4e*8zV3*hsYKbVUDpy*$6eV_11sl(;I;5AOSELy63oIWF0$`2ju$%0_Xji#u?fi9>o3eRiZ_z@#{_#}c8<4+^Oj#7GY_`3d'
    '&PHP~dZlz`8&8ipTx5RC5mNK5ysD3nBqlNrsEn))h$^Gp9;+(LzNM1Iwr%f!{LO?FKU3cSEcq4o=E2Uo-O+nn_ep~m*=c-G+~VGd0Gx-Hw!86QX*YsLWxaW^'
    'q9PPKP|zi0$shcf0IzNU5Z#C~Qs{;;f9>cs!&y?hwVfo|i7h?5?fyiG;XAPysud$$pbZ^=;pFG@i5A@Xk*;H0q*!&<DM-0!o$@i?e4=4F%Gqm|poPxc&hlt}'
    '`qqh-p(nW$BP>_0h#-StNPIPDo-Q~&hF;So6u<zi8KOvepQ&g+HjZ(@EtSJw(0b;j5tq~oznNNztwXs_a(Mp=9|T>YMm2jP<(1^wLvJX?q9?h4H?>{d0je+F'
    '$0k(@4$MuJV#OmCUtb862_Jr=52>oq4RmakUVu??5}sVt6=y`j(=IL~wd&6#C{iE+g>XMPdhz1$$(!!ahsST8zj*#H;PK(963Fpr65pRhyf5yhbCfWKmuN|K'
    '_An?`Or(%KYxVOu9xELemuIPVN&qx86L0OJ$E7eC!M<xP#~pg>Gg3?YTUb*8-^CT00hZV79H&Ovtj)7^rzsS*n!8HYjl|2tkgy}QbH6bnBGUw=NePpKc^`^i'
    'jcEU29s=#vTrP$xpS!&0SZhmeWHC8vvAobwSbCr8-iy~Y54Udm9j_3l=IkDy?{+qzBa1l*0AI(xxRT7eiha=<;;ODHU&YG!^7--c(Q*C7^Is36CokXtJpcLm'
    ';c-+u&CYw*L)=p1(d`~$V9l~VO8MxOG|PGy^RHlMeCd0m^hao=I~y`2)x{7uKzB6!kkL=t+uZ@MH$MIdRHW>O3VL)hqXl(qp`bbW;Q6apFz~|J|Dx@)j_Zmg'
    'IoO0=k4Xvf%f@7X=!*Y$oK>%Lwt(QuvQBqNyqwImFyly`CR#yp__z2&3}-gzYB9BN#~2K1wR*i(+H2}69?x9w^T6X&)YiTQ96@^IWy3}5UoiZ@tXj)Pb4zWZ'
    '-1Z>+nMMNDi(kaD+ok<hIH$B~DPHoi*-E;L_qC*oAghDB9OG$tL8h`kW+myfY|xuW-HTq=dbE^oyTv!3ocD&~m%VAtbT=`bGM~n)5PAGg;cNamJ|?u&5Ujoa'
    '^Yi1AH&N{!(1$_X!Z5G1;eudJr@i59PR`!A3U%BHk;>t5|5w1<pSHa_V3v_`8HrUa1xiRYy?=cGqe1Oyt@6|HZ?B#_>z=$mdQ(Xv=O=n3SAIJ9_3-%j;H%fq'
    '|Mf38ZqJTh<Li@`M@Mg-JwN0J@#lNE6%0G22er0OBxTo4MJ<!NTq>ARx<XEac2?<%n^l_e1(6f94m2;fl5x%LL*H9up<;8X3|NTK<?^}8Tth;uSsM;x&@b-3'
    'PM=+WPj26%BrArfRJdHl3)Bl{E1@uw0Ku0Sl=b39Dwc;!#fcxQ(D|%{^*_{>m64?3M4S}JKC6X*SRpGp`fd&=Vkyeetdt3bVbMtpM>GnKA&I}ld$5qc-<)m}'
    '#a>F;RY8lUo3SR=8C{pE<A<eW{VTEdKfgG7`}&^<Omm$@C~1!Bl!0oL^#*ma9oC=+*{nBm`Fow937Ewma`{-<F@A3)PM9$Sp@K`J)gbq(>DB3I*w?#C@il1l'
    'S@h<KLhePv6b)v*8{Y6&GfFu)zd9AjUh*mh5`nnZz1eVa4igU5Vgv>zav~hyx9FlG_0jkUgy}TP#tH`vrQxvzJffS52Jt@2Zm7?Eg77gGs?MX!tI2{YoTJVX'
    'y<=vQU<!YOs5>O*;2zWl>zAlRebQgT>xPf0MVbx;1x#b+2GN`8YJ?)ZBu8PasKxn^5u||b_f&osa^z+iT6I)f#0n+7%q`-L_lAfLjuQ#e*=YE0_-@wYl%3gl'
    '@DAsZa$U`O=yR@eUG>HUfUK6hKA&cN%#ucHzj^=H`_KP003;QL6hWFUNV9m&YETmVMd%~=$Kfx((C_Cje#QSHSP9~8Vtu&HyKkSrLg+~2xIuH>l5K&ovqK_O'
    'dSjd+9oC<}gwG`hr}He0c6WD8rL4%FPewX-4%aV8@HfNp0L~Y#<!t!w9lAx)VdF|)93DLFK0}s!EAsk@`^Mc!?grrs{`YT3Zw_Uost&6H+PM*IB06pquu5p&'
    'BLdf`qtrfrw}7Kc;d)phjF8~oaF`Euj}XH<>fH#KI8`$5&xTV%4rhBYf9`nb!f%&tJNwu@L#T3!Q2S_N*WhoOG;Ixr2bPejy#w$Y7FQjX$Up-sE~-+g2p+1e'
    '1`{bY0T>1~oLuqI;**BaQAi1^olW>yMbQ()okUz!@Mk416W%p?tqbRX)libt>{^vTwYx$xZ24&m<?FE*WYSjLNT*%VG*mGHL^ctBd$)^Zw2QxM(jxJ5oy6%t'
    'oDc8U2hj~&<gYl2qSA5Wk@tab@iVgKbnbLEaIUT;thp|AT7!@`8#E5L4OJSs)=qH%KedwAgTuO3a9yE^nmvAw+m1;;2w!?~rrx>mvAs7do(2KgH`4-gfDf8m'
    'Av83BPO!=XYyIG1r?9sk4557l3ZotE6R^?-Rgwbpz;-c`5n!KrLP00a<4c6Lr`jzVkF`RS2%*Ty0}(02u$2oP;>aP|lg@_xoSSe}9Zvb~!zDAW3%6T4k3v(f'
    '3IwnpHS%oaP)FtZgK=byMyoLKsDivH5tYh6{xU(u7f{mZ<-tF@N5@YOk59_m?Tuy#rnYYIJa(&sRs)jCEEy*Lyf$Wx+E_}MTmfq;x7{@!e-Zwdh2d2pcTJc='
    'l^`h)6jDBE<dIu|+RP2Lr4eOD#;cjG7_$kLFw@Ue1UK2M`SQYk(Kl*e)+3h<0E&!|W^~GAB?all!pB{K>Z{jkAGk@z3U^ZY1|SiGZBv)jI01yjD!$MVJqd&e'
    '%8b}41)w64(0cru-?N7AUJulTeTTbS+U-kYlFLESIF(<nb`ioYLTiZ&sL<c^HK&)?S$RS}36zG5&UFQ&x^Y%6ariLN_#lpcpjD&4mv&Ean|Tl!<9sg=Xw4*2'
    'XtlWK<3wSjSxhYgsQHZ=+C_f2i;km#a%osue(`|9gosWKX{SKtp@zCq3T}3}xD}+E0$?F6>UrA%zT40H%j9QVB0Ps<^k2qav=!|X(6Gg=t$y>^5@MxuS{APm'
    '@z`7lYV*-<Y<~p@@1~T@amI94c@x{O3@f0+M%yhzFFFPJ*Ae9ZAKhn1za4X;ng>bLd<g&i2>(1vD0k5orxN%F2~CgqPg~|Nc=p$;@kzk!A6}CHQx{RKe||Ma'
    '1Rt#uX>t0}t0_ux=e^OHO2I|xe7G|VMq<F=9PuCc&WqvI1xNlW!9I)nSF;(aRA?4Bw;n!bnQbVF2BG1F+6E)7tSXY+13OdG=#l2KR4ey?7dx{qBm6h>lV^Uk'
    '-eAcn4Dx~El`P}~zBT{rIi>$3%kkgGY!K=F@8>gyM$@+v+pq#(f~~>4)wZMWO(&vlN}9G4|M~0+T*r!CNv#*W9{QyV<`t+zaWla>_@&hG-@xp^5XwWMzR;HJ'
    '<3PJ+V4<rPX({nYVlKido1@%5(6d1&b|a+}OVaY8v{Y>>Ne<rDT$W><SW3jaK=8L*0rHD<vn^`ua~|y{gso=wkEoRIsGL?hB+={I?uM>eeg*CIaxX}ixep|E'
    'GyVg5cdhF`fHt6X1x@2U^wu=za1x>Jgc*8xd0&0;fu-)us!^wJ#umo0dnG}igG_E7n{`rj^;ox4;O2qGHU2UDy$1F%Ze%)2&e`L<CYHLs#l&#AZ6YoVpHrN1'
    'c~y#ih8vCa|1BI(ah<HBZmpxw{(Min*qJ#43@&6Jmb}y<0qR}JA3@4l?g+YbiFM-F^+tdXmpCKbyCcHWgSW5H5n<4~85c_4Q4NvvwxVwz?M332K&f|g-U#<>'
    'k$(ExXd&RFV6xm;9*f!m{&Y>7gQ>Ya;BS3<z~3QDCOj?%t!&*%px=FXA7Z>3`rl&w-(vjVV*KA?{GTDl6J7mVjQ^{O@%pZ7SJW++w>r3mzK+$Q5ZgN-b*p66'
    '(66s5W3MAK7e(>txl^L(YRrTy?&*Q9EAFYNiBgtiIhX8ifC4Ugbr)TzV<nDQ%2^z-?nq)y%DNmee7J-o?!L5`#3piya8R3D@XvNEZ-rNU>GO&g*79Ch%X<;#'
    '6)*m(yyDBhdBwkZ#lLyQzj?(!kym{AH?R0t<`rKWF5se&S9A;gb$G>>{{_6_OP^O<jhS$H#g|{oD_(pVujp=oFXk05R^$~ga=hY8i&uPkS6=bu>pxw43Vg}a'
    '=dW8BlviJzXZ68wN(69(v5o@aOHp*SKT~b`(^I-EBORp3&p2r25&ux3D*Wr|;la}v&tIYU)<b^s<N!lY9`5ijC!7R+yL|L1FjLdfkYEDg?<psWFh>BM&0r~e'
    'a|ShlpCR@d9^W^6y|rVr*AI6aD!uLs2}T0ctjLaQF-o>kR?VB8Sxy-lKUMI$ue9J2M5`&!82p6ksX*WQnKGi<j{ef}G9!(B;i|phQZ%m34bniv3H3>12-n!&'
    'M1{S3OS%8^2gs)EJo4_aK{m4LY`3-)RNCF;5Nmncdd@oDI27B(2eCGX0mRC?nfqe1rE(I`9_})voX!#xq}GC5R;-yZN-9W`WMvh+%EX(T7qb&cA4MIoi#+B%'
    'qt2oi{39zyA2W}Ny~ZxWFrhu455sWF)JZhEdTg_%Ab$GU(y;6OsL9>KfkN{E#>}u!&Jrfkqqr!Ki$=qBx|>91XM4PlV+quor0#Jw`VQ38tX;9_RDcf(?!Emm'
    '9G|_c$_!bsd-o$Dw|})gT$~Vi8K1s<U#WaWjE*H6KOYKUi)B<aC@;8YL;Zq*7f1%@90y04Q!(x@Q7a(l(b|@m$h2=2ApfDv77liEoB%jGDz<c<3vesmudw^d'
    'i_1o`=t}|6P4T`o9x_2R0rzCk4PRLXFz0>bumb+5mI?<-9{B0$*OdnfvO-$2K#u*_!&L157x6%LwahX&P|-$U&@*vYfuWSiS}riStNX<Q1JtpSz#!!;fkAg9'
    'u_k3*fdM}Jvjql(9)E%U7KlJQs-NP1AU_L=QUK->sV+v+|6qdcweavYP~BeJLH{a*-wpKF0sUB5soELThLuIAZQt6CRS{pw{?QhUKiZP9<G{z&KR<cnhmc@7'
    '3`gcKMb$!)Wi6E(#UNJndxH$<TT5bUv+E4D&<+)cYZP^DFv<LMYsU%MZn)CJckq>W>ZxEJxeS%@ONuH|2T#3$-M7fo-0@_dhYaTvvKstz6|=$0LXYO_gW`#f'
    'rSCHCnlN`nXN{wpAR&1Qe!Hv)IZi>P%vKvHC~zrB>RSO*QScMIUmScC9~i|!A;8A+I0QJbF$GtucxoAHIG|b|yU&(P2GuhIW5E-oL3n~dMZWaKf&SR1_Rxv+'
    '#~6PM@XsBqM7I=-^>+jP)wJ7FJtU|q#jlIfbr6Sz2GVv9Npy4~^=<J{%CuV#EvrSjV`QbJhOIpnKYjk}SV@dipkUxhnvXjg#ymDzYHQ`h<yAD=Wh-irT^2?='
    'mj>SX&ZZs<y~HTj^;4hZQnPc{Kd)>d^PSTFQr569Fb*y=T!of%ndM4mpP~Mj+Xi~qz2Qg*big9vw992zGC53zpsi#R<HGy-)CBo@neJMIlmI~ZP<f@gmh?&w'
    '+V!1QN6E0(6Ov@PViIK=n~jjY>tPwbDC4~3NOyj?JURU<ycEwylis4%oo)Zvm9?X(lFy)`9Qi})gz>6GpAlV64|GHKv|h&a_#Khj%6np&z*G-nCjsvg#LxUP'
    '@}gtg`!XAKnDz&`d~hE!k+o^-Y4eyGD#_RRD}uf&P_Bg0<ej5aY$(HueLaH3wW1-UD55)9)RJtm>g6<>0d|UMwl@841S<Thwm6wPN`-7pasT|w$=+rOjO}ej'
    '8N;cASj7TC+l>3}rn!$_Xq$64+C5n3KCWt>`<S=S{nIwk{qxQix<5a_;pEx#!xvBMDB8B7vnya>&Q#?7czDqp{V+ndhKzIwr%pW3aP*;$@+0OC9AS#_`xd)T'
    'UP>lK;$oj1y#+pXr-8<wlV^vAui@7N`t{4v(a9nF+HN#H^Jgy(UOi<`H!QG4|AsF~fQHvNOhUmWdEQ0Ieg5RI`{elW;AIhRE>|I%ThRz8kUtOm&&K*Q5P$|M'
    '(7*?>1rq)+xkOY;uA*Rm0bCbmkf4J*zc7aw{tg)o;qg-GS;*tv?0pU_R{?%+DR!?C6<kt1zO6CjuCrd0tdx}e`03Y1qr#5l^!lMGKnwPA**}oqtU~$CDw5w!'
    'O(@-7wA_I}SkAcNO(}k(AFbl~SF9(vyy^{TJte7@w`TZy)*CPUb?f)$=bFJX-(A2hcFSSTP+Ete{-5TqthsF?3BUVSpu7(tB2Y^*k}Oj}s<g2pb1Od9cB-<)'
    'V!;#z(TGTaOOW!R(tqFSV@?c6P>Q$qA+a!=vuCE~>*=0uQZC3Q>y;=x2}Kj2wbRQ(6fF`IC~L7;#UhIS23p&w7gQo*M4O<nL~DLE2ojIMQSbv3akDsK`YTj$'
    'snUxIKEhZ$mJW(o>^6E~58FwgnX(}}3)UKmZf~$4t2PT!cbhhP$NaG$fa$Vin|;C9H9LjFz~;b^yQ5sN_JiZjz0v3H1Nv;K>$Z2hGL7=4VdsY7JbUW2LXoZ$'
    '-mh&JgPRiu#fO+5RiYh`8L0SA!H*;h!s*D@6dAIgHdLTFVOF*M^Dx4RAWRNm6EBKJ9!cLgI!(9OY`D>6;ah@yqpj$*5ul42s;s&x^+1%J2Nsk95|)c1chvjf'
    '$Fa49oAWYDK>lzpKunrcD+CJZ${aQ*XTY`J-NP?zz<(EVvCPKTwgs;tX#yFs?!U7Q3)-tzO?eyKus|2IA%bmrX-bpW9GDt_?We6y*MMjERDv6}GT2p;bE;z0'
    'Wcx(D`~rawF`{u!>olf=NJpoWWL6K{%hj?4n={%MSZTQ`!4Y)}cIi_%AdH!DZ~Ub#r)U+fmT5`s$z+k*A2qfIHH1&tQU7PMr=q+H*V_=a+Tx`e*+Zqvjo5d)'
    'aA_}~M~jxCjz*Ft=Q9LL)sfgB%C2IiDA-7<41PW62fv{@>xJN^*%vXi;36wm?PXRj#9%TC`3=HhEB)n<7o-)+W<}aN>K@XM?Tezgjsg<om>z-?ELTM_BWg^('
    'T&6knOVp6QeDl6$`Qp#N4*obpc`kf8pwNpFLCC)elE^PO?;v(87XHWYFV4@P_G38VsJ?e^UXd;nKb3@a7ecSdJ04mY;`dZc1AOkwgbb{Kj0_j+OR*!;PY?rB'
    'r*g<2k#NuLpj!Jqp8}XdGs%|S{DYF*pb~u=a0GO*V`jw){sDh|ad4G?fp9m<J>VOj8g%9N5i@<H$N?X*;72afrgM-r7+3iWg?;k3Uar_5d`>Y9Fq3xOhi8|H'
    'P6~%Q&E@_gTh7-j++}5pyNNcC&<pDc1bImzsZ7RQcLRLnT7idkkxNz9cc}J9j=nFZ-a?*l`9jAQWrDf(f1)Fx=u4>7=DMI`4#BrogRvg9KMggl9Cifwk}Hd='
    '<H8dJ(YpVy*cJ9RpNCZio*ja>h=UgV5|h<}VCx7BD{)r1`HNyb{j{p8#<WhXuwb&I84C?O9ZGM@)s>BVBIf@LI9WNSc^N%MbcB_xxQ**~8@eX3O&*<4?_@$z'
    '2i_?prJoL69qk55xvfPci`ya(lAU)FFvOA#7Q|w_9M4O1!+&t_HKk8jl98?NySwh2(#kFC=&$487PsPdbzl@pU&;5%5TL^~Q<YYYqC`z(Ij5Q`4;}VL-uoV7'
    'RZ0VEFfGFEFvo0jHUG?}Apka7i4Uo;Hq4&p<mH;^c7^d*Q%Y}<K1+rTjhV=iZi3oXcG|!axG3;?&y5yf^(*=jYq{dB2)*E$0s|?Cb48q!tFss@{G?U*TDhOG'
    '5p75BtqGZ(KIHu26^S(@%nZw|`;YoyqbgAgCI1{4hq&t%O&{LF%0cYYOF5E|XaFtHP5Qgf2-hGhB4PJDin|Lu5^UmPp%{r^tWvX^gdebj_@~;+W<^y~RiBLG'
    'R!!K&9D5}T!Wqng!)oK|*(!J#T{CW%p}q$OjFYf$S8QJ+ju=5my$<v=6;upSNiGmWBw-Rnd1{j6PsYNMNgjP!gRcF|BL@WPbWsW|4nBB*+)`O@wZSJFNG-?('
    'NNkalZHp^1gCVcz4#aw*EqSGa^a1_L`kRImmh#GBKREm2?LoH_TnPyyhtN^WV7i95R4oX1+&vCHX5wcm`%#J|=^3Os>Xqw!K~qez!SGLvW#tCw#llSlZ{70l'
    'o5W~j=eUY~i%1SMjd;SVv<OLQfmtrcU)ca2Ef5YG`KnYgO-%ast*_zr$bMH%VX4HCYJy%0P0pZ~Lz~0J2_EidMhsaV+Uf{Ll{BFU;Yzy}5@H1_Mru6j`}nKW'
    '+Ti;xP`hB@Yaw2~K6{tGem@M;$xKXKib1@?kxfWc?S!n_i36L+RGk$fSIbnQt5A3-NuY;K$uwY?A+hdmrmkt#c4ISB-9+4Efe<dBXW)3DXwnvK772cgacXaS'
    '-RCK_k&0E)qCaC;F_9(9akMhAir}5yyTfiec>VVG4`jgq9@~JvXx9nh=RzDfOK4LhMHP{3GQYHuKZUCAL!T7|ql$k@@sqO0R@uO`@+4S+FZ(1Q(!vK!n#coY'
    'gZOV}RE?ww-KZ=nL{3_wg1T6RO0n<6H;r)u0fq6gQj23H$3aMHjWCiAbZ#*)yhOh_b}J{voo@AAC_Nx})Jkgswd7T~Zd@_R%M>%f1d3YP-3S&G$3#rHusE=Q'
    '3+x3w!7&7L1YSp3yswN<7=dg^3eq$1(xMa=dE~;Vd5LqIm&6bR08Qz`@7PsL4>@0W1~C^}a-hh?Za^l1v5nwP`v{aSy#sX4FkY?_>ARuk+0ylAc_e)8B)VD@'
    '=;`({1cx7=#T+fEnFQzrYCc71`Qxg9Ua&k3u7Pig&ndK@cudvQl>%x=Vf@tQV!Zmqoxs&Iii5h*#!SB$&qJEz1pglgKm2h0IU06qVx!(<pa0TEfthf_yo#c2'
    'UEoE=PsT`Ap5a~-o%60aC{eSHh&SNP3~pF;j+mTNn~7E4X_;qMh}eKp)QR&O?}-pugA6MQ(;X6e@QNe$NrE@kxU^DQ-Qqm4&YqarU#wK~id{uW-&m|~Qf%7d'
    '7>%^=h4*yABt)o=m|tZ0{N3%38o*795Rbx|2$cwIYSd(-O_jxfn??s>3o~tnoVt}=G3OCs&Q33w0W2s%r6s1?1e~2-6>y5QO_-5#{BrusOXWuZQ*4krS+5KQ'
    '%J?<|0AAvwI-YAS*!WC>uxra~F6fuvOx4+KJ{CgDZ_tgAC3uM6ux+k0n1&X9Tc);Rp}}v2`{W?hnlsXdBHPGPH5-=?UgtW`y3ftye3RvR4>>Tt={Y#29f-e}'
    'Z+#~)z3g_!QA+Mn*srbzhk!_%!O_iF)bqGwqHhBy^1cu_!iSL4=&geXA#lAeQBjwf+3!XvLCYd?Q9eW#QH%F~FN-wulCSAuTdev-6Sb@Q)>lO|(T~QCdIz;a'
    '!lqmMxK=8ud-0;xTh^-=A69gI57hQ>H-SKL2jaQ){6ZJ`Tkx-SwuYe1g5e6Z3O8V&`oQ4btV~+w)BFYk+)h4am+M(}0@@xi-I)w_I}cVxvG41LwKe|(Ey1WI'
    'f8v+K;b<SP-^x}b)l@O<V=S@Z+4o<yC%>OGi}o7h3zSvv7S@%#U$hkaOKg5|7Sq!rWga7_I2rbPBa&ZebOK~lBw{9E&3Nx!ZQgLSK^%Rsn}nLJporlCehaqi'
    'JCTkwTuZAHiV)4t4OU;(!w<dM+Pa0|0*jd6uo$5VFC4|Xe}cAaK<Na@1$}E{=Ehi5GpSHP076>g^Tf%aae>Mr1fW*8gGNwDTAEWjC3~Iv!-{hA#P>J(X26SG'
    'Gk7epm1v852Gi?HA46N0i}5lOQi#AV(0et7{1nRmox?7R@zqIEus90@w_+0j#YbwMaO}fTMVsr>>={tnckZaEF(H^2_p3A2chO#~SB)^Y(c&X9x2Q>CZix<D'
    '%*|OW%&j^QTiBoh=9aDOh`C>#y*n3(vK-H|Hrf+{a#f6HzF>m3aDc^C&^vm57?#1=k3SwL?EUK8eR4n5C|Ue1nDdlwdBunI;QqYPHE$}4eP2WSztlDDR_!pv'
    '4>C-&C68x|M<1WxXvJN)HnR<U*v5vXa3$Uhbf-nT8kl|6+&V{D0*2uWI<sC4;iqA~8jZ;J44w~8vgb{(#mTquZT}lQ*#O(v7Z&64@E%??Ro>%M2&!d1d@2{X'
    'WwPdEpjA&f%;nK`y0$?xNSWj|fL-vtU$&jQ58ImUWasVL`D351O&|Ai&6<bDzgwF!6PFX<yjGi59;=-jZ`ID5GH+S?j;wod9<(mjH<vT86=3xKshDN$$*d^X'
    '%S<xq!MT7B@4*%M)w1}O-GI`dWjvG8Pp6!hR`LNBKe4i2UZKmCfx-Uoo?;JD>!fD4g5R=bA(BYb&1n!&w<ZmZAvlTWkPZF@4Udg{3Ob}ROR-Pi|L~|kDIRuC'
    'DDxkAuI}U>K(QAsZr-80ViUEi8f{bm$bMPCYv*3pc$=4&$vw@iecc59XM6`1+5NGFqR8ah%84YuwH&&xF%F@YX<!GH##m>hPeVvFPel0kIKIGSc7DMljVcBN'
    'VhNR6izj6sENZ_nA?B0`%$!LlZ>qE*1`TDi?&0Uj0S5iD%F0=++Nyc1&a<T+5BLsSp1&%b2EuQzlL&3v=~YT?C;`mMeA7bPUoWQ1oF>^`Uir;s_QkLw)k;fl'
    '%4e?#nO(0Y(7Lh(gi52WuCR++zAN~iOHjKgl#2|MHr2~6*&B8&i{sg97q$ZTz`(L-_={rE>R7sEB;k;<d5mvm1|-<Xn7pkd<=M5DnwsLhgeF#iBx+kRPQ`SR'
    'M$bm|p)~ZKNEU80^4ez<=Axu(R{Q9}tdvxnl}<FwDM!2&0?O5_kG1@}!$7>tWrc$pg)5lr;qm==$Ay7|$HKq{=l6CnXiUSSkzg*7VD3eNc?Ag$3?w*cj0E!?'
    'kl+)613zTrd2rC{i{A@DF4I&i6Vxu|`J`n3VoM?4-`tABXbv^vtLfSJD@aC9($g1%*Yu8sJDOD56PX5d1(n?0tB?1|U6|bf7rG4lD7D66na}gtc$u%jxS~HC'
    '#o=T;gQp#xSYE31J5<HH(+`6;Nq7GczfNDgNDe#r=iAc{FVnYYuTOvb@Ne}y+a&+<%|LW8T^=2$e->hWr=T(~1vwD;Im!4KfHxNLl`<wH;>CIi*Y#N$uZqQb'
    '5%qCZOlQT#cowM6#oV#j?Uiznm+%(TiWj(^)2T|^!X?B(l_*+jQ=Pl}$g(|$e0@XLV-+LCf=PRHzN09Q;#2ffXaD)Zz1|OU&W5VkD8Y)2geNlR=Fumu?tUlk'
    'b>jVJhY?*k+Vv1{6S)rK!%i&ziJmxpphYp-OS&c_bmzJG{P6-9U*<PyxxSd^Whn~L61EtKk6$W>1IY%<J#)4z>Ne9CVv=<F6|yVs*@+^86t$UZ32h*A|0H7j'
    'Afbfdt%PpN?IPUs^o|bV-m_lZJMKh%-+WtJQaM@otQjps*yHIPKkFMhsngjEZVVRy-vncULEtN=t9)6m;Dnoq=@iwB1$Q)9(yCZ5gBIAVbbHahUfh!c{O8p6'
    'SEEa&(?wCtP|Zgrqa-1W1^AqkaP3FcNvQ4|{^S0{yFd6Zdx^T-vVM6*PyP$H|D1;'
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
