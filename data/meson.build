# Install desktop file
install_data(
    'io.elementary.goaltracker.desktop',
    install_dir: get_option('datadir') / 'applications'
)

# Install metainfo file
install_data(
    'io.elementary.goaltracker.metainfo.xml',
    install_dir: get_option('datadir') / 'metainfo'
)

# Install screenshots
install_data(
    'screenshots' / '1.png',
    install_dir: get_option('datadir') / 'metainfo' / 'screenshots'
)
install_data(
    'screenshots' / '2.png',
    install_dir: get_option('datadir') / 'metainfo' / 'screenshots'
)
install_data(
    'screenshots' / '3.png',
    install_dir: get_option('datadir') / 'metainfo' / 'screenshots'
)

icon_sizes = ['16', '24', '32', '48', '64', '128']

foreach i : icon_sizes
    install_data(
        'icons' / i + '.svg',
        install_dir: get_option('datadir') / 'icons' / 'hicolor' / i + 'x' + i / 'apps',
        rename: meson.project_name() + '.svg'
    )
    install_data(
        'icons' / i + '.svg',
        install_dir: get_option('datadir') / 'icons' / 'hicolor' / i + 'x' + i + '@2' / 'apps',
        rename: meson.project_name() + '.svg'
    )
endforeach