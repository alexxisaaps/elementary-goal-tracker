project('io.github.alexxisaapps.elementary_goal_tracker',
        version: '1.2.0',
        meson_version: '>= 0.57.0'
)

prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
pkgdatadir = join_paths(datadir, 'goaltracker')
pythondir = pkgdatadir

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

# Install main Python files
install_data(
    [
        'src/__init__.py',
        'src/application.py',
        'src/window.py',
        'src/config.py'
    ],
    rename: [
        'goaltracker/__init__.py',
        'goaltracker/application.py',
        'goaltracker/window.py',
        'goaltracker/config.py'
    ],
    install_dir: pythondir
)

# Install widgets
install_data(
    [
        'src/widgets/__init__.py',
        'src/widgets/goal.py',
        'src/widgets/step.py'
    ],
    rename: [
        'goaltracker/widgets/__init__.py',
        'goaltracker/widgets/goal.py',
        'goaltracker/widgets/step.py'
    ],
    install_dir: pythondir
)

# Install dialogs
install_data(
    [
        'src/dialogs/__init__.py',
        'src/dialogs/about_dialog.py',
        'src/dialogs/confirm_dialog.py',
        'src/dialogs/goal_dialog.py',
        'src/dialogs/list_dialog.py',
        'src/dialogs/settings_dialog.py'
    ],
    rename: [
        'goaltracker/dialogs/__init__.py',
        'goaltracker/dialogs/about_dialog.py',
        'goaltracker/dialogs/confirm_dialog.py',
        'goaltracker/dialogs/goal_dialog.py',
        'goaltracker/dialogs/list_dialog.py',
        'goaltracker/dialogs/settings_dialog.py'
    ],
    install_dir: pythondir
)

# Install services
install_data(
    [
        'src/services/__init__.py',
        'src/services/settings.py',
        'src/services/list_manager.py',
        'src/services/daily_quote.py'
    ],
    rename: [
        'goaltracker/services/__init__.py',
        'goaltracker/services/settings.py',
        'goaltracker/services/list_manager.py',
        'goaltracker/services/daily_quote.py'
    ],
    install_dir: pythondir
)

# Create required directories
run_command('mkdir', '-p', 
    meson.current_build_dir() / 'goaltracker/widgets',
    meson.current_build_dir() / 'goaltracker/dialogs',
    meson.current_build_dir() / 'goaltracker/services',
    check: true
)

# Install main script
install_data(
    'main.py',
    install_dir: pkgdatadir,
    install_mode: 'rwxr-xr-x'
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