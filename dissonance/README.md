## INTRO

Dissonance is a vendor-agnostic network-device health-check tool (say that fast 10 times).

## TODO
- Refactor the snapshot directories. I need to add specifications for "ios-xr" specifically in the names,
  as well as add a "junos" directory under Juniper to get the dynamic module loading to be clean. 
  This will require yet another YAML file so I can define model -> OS name relationships
- Need to stop hardcoding paths (e.g., tons of ./storage and ./testfiles file paths that are hardcoded. Super ugly, but need initial release done by yesterday) 
  
## NOTES
- You need to change /etc/jsnapy/jsnapy.cfg



## MISC
```
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
```
