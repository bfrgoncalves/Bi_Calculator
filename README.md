# Bi_Calculator

Belonging Index Calculator

Calculate the belonging index of a set of allelic profiles directly from the 
profiles or from a distance matrix, in combination with a classification file.

### Input files (tab delimited):

    - distance matrix
    - profile file
    - classification file
   
### Output files:

    - html plot with average of Bi per classification and plot with global Bi
    

Test:
    
    python3 app.py -o data -p data/wg_p.tab -c data/class_wg.txt
    
Arguments:

   ```
  -h, --help            show this help message and exit
  -o OUTDIR, --output-dir OUTDIR
                        Path for output directory (default: .)
  -d DM, --distance-matrix DM
                        Path to distance matrix file (default: None)
  -c C, --classification C
                        Path to classification file (Tab separated) (default:
                        None)
  -p P, --profiles P    Path to profiles file (Tab separated) (default: None)
  
  ``
