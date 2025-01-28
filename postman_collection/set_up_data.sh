case "$OSTYPE" in
    msys*)    python=python ;;
    cygwin*)  python=python ;;
    *)        python=python3 ;;
esac

cd ../yatube_api/
$python manage.py migrate
$python manage.py flush --no-input
echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
     u, _ = User.objects.get_or_create(username='root'); u.is_superuser = True; u.is_staff = True; u.email = 'root@admin.ru'; u.set_password('5eCretPaSsw0rD'); u.save(); \
     u, _ = User.objects.get_or_create(username='regular_user'); u.is_superuser = False; u.is_staff = False; u.email = 'user@not-admin.ru'; u.set_password('iWannaBeAdmin'); u.save(); \
     u, _ = User.objects.get_or_create(username='second_user'); u.is_superuser = False; u.is_staff = False; u.email = 'second@not-admin.ru'; u.set_password('5eCretPaSsw0rD'); u.save(); \
     from posts.models import Group; Group.objects.get_or_create(title='TestGroup', slug='test-group', description='Some text.');" | $python manage.py shell >/dev/null 2>&1
echo "Setup done."
