const username = "dev";
const password = "dev";
const door_id = "001b823d-1f5c-4f39-9e74-015bb2dcef8f"

async function fetchToken(url) {
  try {
    const response = await fetch(url, {method: 'POST'});
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
    return null;
  }
}

async function post_authorized(url, method, token, body = {}) {
    try {
      const response = await fetch(url, {
        method: method, // or any other HTTP method you need
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: {},
      });

      if (!response.ok) {
        console.log(response)
        throw new Error('Network response was not ok');
      }

      return await response.json();
    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
      return null;
    }
}
async function main() {
  try {
    // get token with valid creds
    console.log('--------------------Getting token')
    const result = await fetchToken(`http://localhost:8000/token?username=${username}&password=${password}`);
    const token = result.access_token

    // we open the door with the token
    console.log('--------------------Opening the door')
    const door_open_response = await post_authorized(`http://localhost:8000/open?door_id=${door_id}`, "POST", token)
    console.log(door_open_response)

  } catch (error) {
    console.error('There was a problem processing the data:', error);
  }
}

main()

