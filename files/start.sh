#!/bin/sh

export FLASK_APP="server/app:create_app()"
export FLASK_ENV=PRODUCTION

case $1 in
    start)
        cd /usr || exit 1

        flask run --host '0.0.0.0' --port 6060 &
        ;;
    stop)
        killall -9 python3
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    status)
        if pgrep -f "flask run" > /dev/null; then
            echo "SLN service is running."
        else
            echo "SLN service is not running."
        fi
        ;;
    *)
        echo "Usage : $0 [start|stop|restart|status]"
        ;;
esac
