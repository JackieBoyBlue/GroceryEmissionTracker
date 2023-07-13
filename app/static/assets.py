from flask_assets import Bundle

bundles = {
    'js': Bundle(
        'bootstrap/js/popper.js',
        'bootstrap/js/bootstrap.js',
        'js/htmx.min.js',
        filters='jsmin',
        output='gen/script.%(version)s.js'
    ),

    'css': Bundle(
        'scss/main.scss',
        filters='libsass',
        depends='scss/*.scss',
        output='gen/style.%(version)s.css'
    )
}