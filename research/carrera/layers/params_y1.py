
# ---------------------------------------------------------------------------
# V10_CarreraGT research override (y1): cha22's V233 six-sheep investment also qualifies with one yarn store
# (the base requires two). Same code as the base's first _v233_eligible otherwise; bound in the base namespace.
_CG_Y1_SRC = r'''
def _cg_v233_eligible_y1(obs,native):
    farm=obs['farms'][obs['player']];prices=obs['market']['prices']
    if len(farm['tiles'])!=10 or set(farm['unlocked_quadrants'])!={'NW','NE','SW'}:return False
    if obs['town']['unlocked_shops'].count('YARN_STORE')<CG_V233_MIN_YARN or prices['WOOL']<220 or prices['WHEAT']>45:return False
    if any(farm['tiles'][y][x]!='LOCKED' for y in (5,6) for x in range(5,8)):return False
    if obs['private']['shed'].get('SHEEP',0) or any(i.get('SHEEP',0) for i in obs['private']['inventories']):return False
    for day in range(12,30):
        for a in _v219_native_day(native,day):
            if any(o and (o[0]=='BUY_LAND' or o[:2]==['BUY_ANIMAL','SHEEP']) for o in a.get('market',[])):return False
            if any(c and c[0] in ('PICKUP','PLACE') and len(c)>1 and c[1]=='SHEEP' for c in [a.get('farmer')]+a.get('hands',[])):return False
    return True
'''
_BASE_NS["CG_V233_MIN_YARN"] = 1
exec(compile(_CG_Y1_SRC, "cg_y1", "exec"), _BASE_NS)
_BASE_NS["_VE_ELIGIBLE"] = _BASE_NS["_cg_v233_eligible_y1"]
