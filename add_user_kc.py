import click
import requests
import sys

@click.command()
@click.option("--kc-url", prompt="Keycloak URL", help="Keycloak root URL")
@click.option("--kc-admin", prompt="Admin user", help="Keycloak admin username")
@click.option("--kc-admin-pass", prompt="Admin password", hide_input=True, help="Keycloak admin password")
@click.option("--realm", default="myrealm", help="Realm to add the user to")
@click.option("--group", prompt="Group", help="Group to add the user to")
@click.option("--username", prompt="Username", help="Username for the new user")
@click.option("--password", prompt="Password", hide_input=True, help="Password for the new user")
@click.option("--firstname", prompt="First Name", help="First name of the new user")
@click.option("--lastname", prompt="Last Name", help="Last name of the new user")
@click.option("--email", prompt="Email", help="Email address of the new user")

def add_user_to_keycloak(kc_url, kc_admin, kc_admin_pass, username, password, firstname, lastname, email, realm, group):
    """
    Add a user to Keycloak.
    """
    # Get an access token for the Keycloak admin API.
    # This is a one-time setup step to get the access token.
    resp = requests.post(
        f"{kc_url}/realms/master/protocol/openid-connect/token",
        data={
            "client_id": "admin-cli",
            "username": kc_admin,
            "password": kc_admin_pass,
            "grant_type": "password"
        }
    )
    resp.raise_for_status()
    data = resp.json()
    access_token = data["access_token"]

    # Predefine authorization headers for later use.
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # Check if the realm exists.
    resp = requests.get(
        f"{kc_url}/admin/realms/{realm}",
        headers=auth_headers,
    )
    if resp.status_code != 200:
        sys.exit(f"Realm {realm} does not exist.")
        return
    else:
        resp.raise_for_status()
    
    # Check if the group exists.
    resp = requests.get(
        f"{kc_url}/admin/realms/{realm}/groups",
        headers=auth_headers,
    )
    resp.raise_for_status()
    groups = [g["name"] for g in resp.json()]
    if group not in groups:
        sys.exit(f"Group {group} does not exist in realm {realm}.")
        return
    
    # Check if the user already exists.
    resp = requests.get(
        f"{kc_url}/admin/realms/{realm}/users",
        headers=auth_headers)
    users = [user["username"] for user in resp.json()]
    if username in users:
        sys.exit(f"User {username} already exists in realm {realm}.")
        return

    # Check if the user email already exists.
    resp = requests.get(
        f"{kc_url}/admin/realms/{realm}/users",
        headers=auth_headers,
    )
    resp.raise_for_status()
    check_email = [e["email"] for e in resp.json()]
    if email in check_email:
        sys.exit(f"Email address {email} already exists in realm {realm}.")
        return 

    # Create the user.
    user_settings = {
        "username": username,
        "firstName": firstname,
        "lastName": lastname,
        "email": email,
        "emailVerified": True,
        "enabled": True,
        "groups": [group],
        "credentials": [{
            "type": "password",
            "value": password,
            "temporary": False,
        }]
    }
    resp = requests.post(
        f"{kc_url}/admin/realms/{realm}/users",
        json=user_settings,
        headers=auth_headers,
    )
    resp.raise_for_status()
    print(f"User {username} created successfully in realm {realm}.")

# <-- Main entry point for the script -->
if __name__ == '__main__':
    add_user_to_keycloak()
