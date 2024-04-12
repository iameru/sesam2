export type Door = {
  'uuid': string,
  'name': string,
}

type DoorGrant = {
  door_uuid: string
  weekday: number
  grant_start: string
  grant_end: string
  name: string
}

export type UserType = {
  name: string,
  exp: number,
  door_grants: DoorGrant[],
  is_admin: boolean,
}
