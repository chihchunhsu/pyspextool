from pyspextool import config as setup
from pyspextool.extract import config as extract
from pyspextool.io.check import check_parameter
from pyspextool.io.files import extract_filestring
from pyspextool.extract.load_image import load_image
from pyspextool.extract.make_spatial_profiles import make_spatial_profiles
from pyspextool.extract.locate_aperture_positions import locate_aperture_positions
from pyspextool.extract.select_orders import select_orders
from pyspextool.extract.trace_apertures import trace_apertures
from pyspextool.extract.define_aperture_parameters import define_aperture_parameters
from pyspextool.extract.extract_apertures import extract_apertures


def do_all_steps(files, verbose=None):
    """
    To extract spectra from images in a loop after parameters are set.

    Parameters
    ----------
    files : str or list
        If type is str, then a comma-separated string of full file names, 
        e.g. 'spc00001.a.fits, spc00002.b.fits'.

        If type is list, then a two-element list where
        files[0] is a string giving the prefix.
        files[1] is a string giving the index numbers of the files.

    verbose : {None, True, False}, optional
        Set to True/False to override config.state['verbose'] in the 
        pyspextool config file.  

    Returns
    -------
    None.  Writes FITS files to disk.

    """

    #
    # Check if we can proceed
    #

    if extract.state['extract_done'] is False:
        message = 'Previous steps not completed.'
        print(message)
        return

    #
    # Check parameter
    #

    check_parameter('do_all_steps', 'files', files, ['str', 'list'])

    check_parameter('do_all_steps', 'verbose', verbose, ['NoneType','bool'])    


    #
    # Check the qa and verbose variables and set to system default if need be.
    #

    if verbose is None:
        verbose = setup.state['verbose']
    
    #
    # Figure out how many files we are talking about
    #

    if extract.state['filereadmode'] == 'filename':

        files = extract_filestring(files, 'filename')

    else:

        files = extract_filestring(files[1], 'index')

    nfiles = len(files)

    # Test for even-ity if the mode is A-B

    if nfiles % 2 != 0 and extract.state['reductionmode'] == 'A-B':
        message = 'The number of images must be even.'
        raise ValueError(message)

    if extract.state['reductionmode'] == 'A-B':

        nloop = int(nfiles / 2)

    else:

        nloop = int(nfiles)

    #
    # Start the loop
    #

    for i in range(nloop):

        if extract.state['reductionmode'] == 'A-B':
            subset = files[i * 2:i * 2 + 2]

        if extract.state['reductionmode'] == 'A':
            subset = files[i]

        #
        # Load the data
        #

        load_image([extract.state['prefix'], subset], extract.load['flatfile'],
                   extract.load['wavecalfile'],
                   flat_field=extract.load['doflat'],
                   linearity_correction=extract.load['doflat'],
                   qa_plot=extract.load['qaplot'],
                   qa_file=extract.load['qafile'],
                   qa_plotsize=extract.load['qaplotsize'],
                   reduction_mode=extract.state['reductionmode'],
                   do_all_steps=True, verbose=extract.load['verbose'])

        extract.state['load_done'] = True

        #
        # Make the Profiles
        #

        make_spatial_profiles(verbose=extract.profiles['verbose'],
                              qa_plot=extract.profiles['qaplot'],
                              qa_file=extract.profiles['qafile'],
                              qa_plotsize=extract.profiles['qaplotsize'])

        extract.state['profiles_done'] = True

        #
        # Locate the Aperture Positions
        #

        locate_aperture_positions(extract.apertures['apertures'],
                                  method=extract.apertures['method'],
                                  qa_plot=extract.apertures['qaplot'],
                                  qa_plotsize=extract.apertures['qaplotsize'],
                                  qa_file=extract.apertures['qafile'],
                                  verbose=extract.apertures['verbose'])

        extract.state['apetures_done'] = True

        #
        # Select orders
        #

        select_orders(include=extract.orders['include'],
                      exclude=extract.orders['exclude'],
                      include_all=extract.orders['include_all'],
                      verbose=extract.orders['verbose'],
                      qa_plot=extract.orders['qaplot'],
                      qa_plotsize=extract.orders['qaplotsize'],
                      qa_file=extract.orders['qafile'])

        extract.state['select_done'] = True

        #
        # Trace apertures
        #

        trace_apertures(fit_degree=extract.trace['fitdeg'],
                        step_size=extract.trace['step'],
                        summation_width=extract.trace['sumwidth'],
                        centroid_threshold=extract.trace['centhresh'],
                        fwhm=extract.trace['fwhm'],
                        verbose=extract.trace['verbose'],
                        qa_plot=extract.trace['qaplot'],
                        qa_plotsize=extract.trace['qaplotsize'],
                        qa_file=extract.trace['qafile'])

        extract.state['trace_done'] = True

        #
        # Define aperture parameters
        #

        define_aperture_parameters(extract.parameters['apradii'],
                                   psf_radius=extract.parameters['psfradius'],
                                   bg_radius=extract.parameters['bgradius'],
                                   bg_width=extract.parameters['bgwidth'],
                                   bg_regions=extract.parameters['bgregions'],
                                   bg_fit_degree=extract.parameters['bgdeg'],
                                   qa_plot=extract.parameters['qaplot'],
                                   qa_plotsize=extract.parameters['qaplotsize'],
                                   qa_file=extract.parameters['qafile'])

        extract.state['apertures_done'] = True

        #
        # Extract apertures
        #

        extract_apertures(verbose=extract.extract['verbose'])

        #
        # Set the done variable

        extract.state['extract_done'] = True

        if verbose is True:

            print('Do All Steps Complete.')

        
        #
    # Things proceed differently depending on whether you are extracting a
    # point source or an extended source
    #
