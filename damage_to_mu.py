"""
damage_to_mu.py
Author: Samuel B. Kachuck
Date: April 2022

Automate the running of BISICLES ASE using a parameterized damage-based muCoeff
"""
import sys
import os
import subprocess
import numpy as np

from amrfile import io as amrio

BISICLES_HOME=os.environ["BISICLES_HOME"]
PYTHONF=BISICLES_HOME+'/bin/pythonf2d.Linux.64.CC.ftn.OPT.ex'
BISICLES_EXEC=BISICLES_HOME+'/BISICLESdamage-public/code/driver2d.Linux.64.CC.ftn.OPT.MPI.PETSC.ex'


# Write python script
linscriptbase='''def dam_mu(dam, *etc):
    mu = (dam - {2})/(1 - {2})
    mu *= (1-{1})
    mu = 1 - mu
    mu = {0}*min(max(mu, 0), 1)
    return mu'''

if __name__=='__main__':
    params = sys.argv[1:4]

    NAME = 'linear_mu_{}_{}_{}'.format(*params)

    # Make a directory to contain the run
    subprocess.call(['mkdir','-p',NAME])

    # Write the damage -> muCoeff script
    with open('tmp.py', 'w') as f:
        f.writelines(linscriptbase.format(*params))

    # Compute muCoeff from damage, cell-wise
    cmd = [PYTHONF,'damage.mu1.2d.hdf5',
            NAME+'/'+'linear_mu.2d.hdf5',  
            'tmp', 'dam_mu', 'damage', 'mu']
    subprocess.call(cmd)
    # Remove the temporary python script
    subprocess.call(['rm','tmp.py'])
    # Copy the jobfile and input file into the directory
    subprocess.call(['cp', 'scripts/job.ase_bmach.inverse.cori-haswell', NAME])
    subprocess.call(['cp', 'scripts/inputs.ase_bmach.inverse', NAME])

    # Run BISICLES for 1 step to compute velovities
    os.chdir(NAME)
    subprocess.call(['sbatch', 'job.ase_bmach.inverse.cori-haswell'])
    os.chdir('./')


    # Load in computed velocities
    amrID = amrio.load(NAME+'/plot.ase_bmach.inverse.000000.2d.hdf5')
    lo,hi = amrio.queryDomainCorners(amrID, 3)
    xh,yh,xVel = amrio.readBox2D(amrID, 3, lo, hi, 'xVel', 0)
    xh,yh,yVel = amrio.readBox2D(amrID, 3, lo, hi, 'yVel', 0)
    amrio.free(amrID)

    print(np.diff(xh)[0])
