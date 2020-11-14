# Documentation

In this README, I am documenting all the little steps I have taken to complete this project, from environment setup to assumptions made and how to test.

### Setting up the environment

If `virtualenv` is not installed, run the following commands to install, then create a virtual environment.

    pip install virtualenv

    python -m venv venv
    
Assuming you are on a linux OS through the bash terminal, run the following
    
    source venv/bin activate

Then install the requirements.

    pip install -r requirements.txt
    
Run the following command to making this environment accessible for the Jupyter Notebook.

    python -m ipykernel install --user --name=postcode_pipeline_venv
    
Side note: I had an error in running jupyter notebook, which was that the `jupyter-notebook` command could not be found. This was resolved by upgrading the `jupyter` package through `pip` as follows.

    pip install --upgrade jupyter
    
   
### Development Approach

My beginning approach was to first explore the data in a jupyter notebook, check out the quality of it to know whether any cleaning was necessary. I will also use this phase to put together ideas of how I may go about solving the problem, namely the general structure of functions/classes I will use and how they should hang together and decide the expected behaviour for them. This will also be the phase where I discern the ambiguities and decide on what assumptions if any I think are necessary.

Once I have a clear idea of the shape of the solution and it's expected behaviour, and also a clear idea of what should be returned, I can write up the tests that will check all that, then get to work on filling in the functionality. I expect I will already have pieces of the code worked out in exploration phase.

### Assumptions

Below is the full list of consciously made assumptions:

1. All the original data must be returned plus the extra 2 columns.
2. Records should match up both on longitude/latitude and registration date within the postcode introduced and terminated range (former inclusive, latter exclusive).
3. Location strings will be comma separated with the last value being the postcode if there is one.
4. Pairs of longitude and latitudes must be within 1 metre to count as matched. 