from loader import admin_list


def check_admin(id: int) -> bool:
    return str(id) in admin_list

