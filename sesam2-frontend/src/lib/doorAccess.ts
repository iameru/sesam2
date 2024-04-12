import type { Door, UserType } from '../lib/types';


export function getCurrentlyValidDoors(user: UserType, date: Date): Door[] {

  const result: Door[] = []
  user.door_grants.forEach( grant => {
    const nowTime= date.toTimeString().split(' ')[0]
    if (!(grant.weekday == date.getDay())) {
      return
    }
    if (!(grant.grant_start <= nowTime && nowTime <= grant.grant_end)) {
      return
    }
    result.push({
      'uuid': grant.door_uuid,
      'name': grant.name,
    })
  })
  return result
}
