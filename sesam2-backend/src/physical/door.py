from uuid import UUID

def open(door_id: UUID) -> bool:
    """ TODO IMPLEMENT """
    from time import sleep
    print(f"Opening door {door_id}")
    sleep(0.25)
    return True
