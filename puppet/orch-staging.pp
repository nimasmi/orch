# vim:ts=4 sw=4 et:
class wagtail::site::staging::orch inherits wagtail::site::staging {
    wagtail::app { 'orch':
        ip               => $::wagtail::site::staging::ats_ip,
        ip6              => $::wagtail::site::staging::ats_ip6,
        manage_ip        => false,
        manage_db        => true,
        manage_user      => true,
        manage_settings  => false,
        settings         => 'orch/settings',
        wsgi_module      => 'orch.wsgi',
        requirements     => 'requirements.txt',
        servername       => 'orch-staging.torchboxapps.com',
        alias_redirect   => false,
        ats              => true,
        codebase_project => '', # CHANGEME
        codebase_repo    => '', # CHANGEME
        git_uri          => 'CODEBASE',
        django_version   => '1.7',
        staticdir        => "static",
        mediadir         => "media",
        deploy           => [ '@admin', '@wagtail' ], # CHANGEME
        python_version   => '3.4',
        pg_version       => '9.4',
        manage_daemons   => [
            'celery worker -C -c1 -A orch',
            'celery beat -A orch -C -s $TMPDIR/celerybeat.db --pidfile=',
        ],
        admins           => {
            # CHANGEME
            # List of users to send error emails to. Eg:
            # 'Joe Bloggs' => 'joe.bloggs@torchbox.com',
        },
        nagios_url       => '',
        http_cache       => {
            enable => true,
        },
        ssl              => {
            mode => 'redirect',
            site => 'star.torchboxapps.com',
        },
        auth => {
            enabled       => true,
            hosts         => [ 'tbx' ],
            users         => {
                # CHANGEME
                # This is the credentials for HTTP authentication. Eg:
                # 'username'  => 'password',
            },
        },
    }
}
