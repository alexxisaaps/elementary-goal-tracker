project('io.github.alexxisaapps.elementary_goal_tracker',
        version: '0.1.0',
        meson_version: '>= 0.57.0'
)

prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
pkgdatadir = join_paths(datadir, 'goaltracker')

# Find glib-compile-resources executable
glib_compile_resources = find_program('glib-compile-resources')

# Custom target to compile the GResource file
custom_target('gresource',
    input: 'data/gresource.xml',
    output: 'resources.gresource',
    command: [
        glib_compile_resources,
        '--sourcedir=@CURRENT_SOURCE_DIR@/data',
        '--target=@OUTPUT@',
        '@INPUT@'
    ],
    install: true,
    install_dir: pkgdatadir
)

# Install Python files
install_data(
    'src' / 'goal_tracker.py',
    install_dir: pkgdatadir
)

# Install quotes.json
install_data(
    'quotes.json',
    install_dir: pkgdatadir
)

# Configure the launcher script
conf_data = configuration_data()
conf_data.set('PYTHON', find_program('python3').full_path())
conf_data.set('PKGDATADIR', pkgdatadir)

configure_file(
    configuration: conf_data,
    input: 'goaltracker.in',
    output: 'io.github.alexxisaapps.elementary_goal_tracker',
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)

# Include the data subdirectory for icons and desktop file
subdir('data')