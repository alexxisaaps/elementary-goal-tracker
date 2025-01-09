project('io.elementary.goaltracker',
        version: '0.1.0',
        meson_version: '>= 0.57.0'
)

prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
pkgdatadir = join_paths(datadir, 'goaltracker')

# Install Python files
install_data(
    'src' / 'goal_tracker.py',
    install_dir: pkgdatadir
)

# Install data files
install_data(
    'data' / 'style.css',
    install_dir: pkgdatadir
)

# Configure the launcher script
conf_data = configuration_data()
conf_data.set('PYTHON', find_program('python3').full_path())
conf_data.set('PKGDATADIR', pkgdatadir)

configure_file(
    configuration: conf_data,
    input: 'goaltracker.in',
    output: 'io.elementary.goaltracker',
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

# Include the data subdirectory for icons and desktop file
subdir('data')
