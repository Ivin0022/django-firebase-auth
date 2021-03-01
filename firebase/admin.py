from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from firebase_admin import auth as firebase_auth
from django.db import IntegrityError

# local
from .models import FirebaseUser


def firebase_create_user(obj):
    '''Function to create a new user in Firebase app
    1)on creating a new user from admin panel (or)
    2)to create firebase user for existing users in django db'''
    try:
        data = {'uid': str(obj.uid)}
        if obj.phone_number:
            data.update({'phone_number': f'+{obj.phone_number.country_code}{obj.phone_number.national_number}'})
        if obj.email:
            data.update({'email': obj.email})
        firebase_auth.create_user(**data)
    except firebase_auth.UidAlreadyExistsError:
        msg = "Uid already exists"
        raise IntegrityError(msg)


def create_firebaseuser_from_admin(FirebaseUserModel, request, queryset):
    '''To create a user in firebase corresponding to selected existing user in our Admin panel'''
    for obj in queryset:
        firebase_create_user(obj)


def delete_firebase_user(obj):
    '''To delete a user from firebase on deleting it from our database'''
    try:
        print('Deleting uid from firebase - ', obj.uid)
        firebase_auth.delete_user(obj.uid)
    except:
        pass


#Action Description to display in Admin panel Actions
create_firebaseuser_from_admin.short_description = 'Create Firebase Users for selected users'


@admin.register(FirebaseUser)
class FirebaseUserAdmin(BaseUserAdmin):
    '''Admin View for FirebaseUser'''

    list_display = (
        'identifer',
        'phone_number',
        'email',
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    fieldsets = (
        (
            None,
            {
                'fields': ('uid', 'password'),
            },
        ),
        (
            'Personal info',
            {
                'fields': ('display_name', 'phone_number', 'email'),
            },
        ),
        (
            'Permissions',
            {
                'fields': (
                    ('is_active', 'is_staff', 'is_superuser'),
                    ('groups', 'user_permissions'),
                ),
            },
        ),
        (
            'Important dates',
            {
                'fields': ('last_login', 'date_joined'),
            },
        ),
    )

    add_fieldsets = ((
        None,
        {
            'fields': ('display_name', 'phone_number', 'email', 'password1', 'password2'),
        },
    ),)

    search_fields = ('uid', 'display_name', 'phone_number', 'email')
    ordering = (
        '-date_joined',
        'display_name',
    )
    actions = [
        create_firebaseuser_from_admin,
    ]

    def save_model(self, request, obj, form, change):
        if not obj.id:
            '''To create a user in firebase, on creating a new user from admin'''
            firebase_create_user(obj)
        elif change:
            '''To update a existing user in firebase,to add/change phone_number and(or) email
            when changed from admin panel'''
            try:
                firebase_auth.get_user(obj.uid)
                data = {}
                if 'phone_number' in form.changed_data:
                    data.update(
                        {'phone_number': f'+{obj.phone_number.country_code}{obj.phone_number.national_number}'}
                    )
                if 'email' in form.changed_data:
                    data.update({'email': obj.email})
                if data:
                    updated = firebase_auth.update_user(obj.uid, **data)
            except:
                pass
        super().save_model(request, obj, form, change)

    def delete_queryset(self, request, queryset):
        '''To delete firebase users on deleting users from admin panel- bulk delete action'''
        dict_uids = queryset.values('uid')
        uids = [item['uid'] for item in dict_uids]
        try:
            firebase_auth.delete_users(uids)
        except:
            pass
        queryset.delete()

    def delete_model(self, request, obj):
        '''To delete firebase user on deleting a single user from admin panel- object level deletion'''
        delete_firebase_user(obj)
        obj.delete()