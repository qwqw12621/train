jovyan@vm-j4wlboxamd59:~$ python verify.py greedy_opt.py D0000000.in 8 D0000000.out 
Traceback (most recent call last):
  File "/home/jovyan/verify.py", line 46, in <module>
    main()
  File "/home/jovyan/verify.py", line 7, in main
    d = open(infile, 'rb').read().split(); N = int(d[0]); T = int(d[1]); pos = 2
                                               ^^^^^^^^^
ValueError: invalid literal for int() with base 10: b'import'
jovyan@vm-j4wlboxamd59:~$ python verify.py greedy_opt.py D0000000_tight.in 8 D0000000_tight.out 
Traceback (most recent call last):
  File "/home/jovyan/verify.py", line 46, in <module>
    main()
  File "/home/jovyan/verify.py", line 7, in main
    d = open(infile, 'rb').read().split(); N = int(d[0]); T = int(d[1]); pos = 2
                                               ^^^^^^^^^
ValueError: invalid literal for int() with base 10: b'import'
jovyan@vm-j4wlboxamd59:~$ 
