| agent | cha22 | emu_eager | emu_eager_m | v4 | v6 | wins/200 | mean |
|---|---|---|---|---|---|---|---|
| v6 | 37-3-0 (+650) | 16-24-0 (-140) | 36-4-0 (+559) | 36-4-0 (+609) | 0-1-39 (-17) | 144 | +332 |
| champ_nt | 35-5-0 (+1787) | 32-8-0 (+1182) | 36-4-0 (+1760) | 35-5-0 (+1756) | 33-7-0 (+1424) | 171 | +1582 |
| c028 | 34-6-0 (+579) | 27-13-0 (-18) | 35-5-0 (+540) | 34-6-0 (+538) | 32-8-0 (+205) | 162 | +369 |
Traceback (most recent call last):
  File "C:\Users\Admin\Documents\Kaggle\kaggriculture\gold\arena\famvs.py", line 72, in <module>
    main()
  File "C:\Users\Admin\Documents\Kaggle\kaggriculture\gold\arena\famvs.py", line 64, in main
    row = run(path, name, workers)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Admin\Documents\Kaggle\kaggriculture\gold\arena\famvs.py", line 40, in run
    d = json.load(open(js))
                  ^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\Admin\\Documents\\Kaggle\\kaggriculture\\gold\\arena\\games\\fam_stack3_emu_eager_m.json'
