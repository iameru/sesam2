import Config from './config';
import store from './store/store';

export async function makeLoginRequest(username: string, password: string) {
  try {
    const response = await fetch(Config.apiUrl + '/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {

      const data = await response.json();
      store.loggedIn.set(true);
      store.accessToken.set(data.access_token);
      const decodedToken = JSON.parse(atob(data.access_token.split('.')[1]))
      store.user.set(decodedToken);
      return decodedToken;

    } else {
      throw new Error('Login failed');
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
