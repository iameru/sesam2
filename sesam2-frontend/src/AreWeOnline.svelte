<script lang='ts'>
import store from './store/store.ts';
import { onMount } from 'svelte';
import Config from './config.ts';

let statusCode = null;

async function makeRequest(): number {
  try {
    const response = await fetch(Config.apiUrl + '/are-we-online');
    statusCode = response.status;
  } catch (error) {
  }
  return statusCode
}

function renderStatusIconColor(statusCode) {
  if (statusCode == 200) {
    return 'bg-green-800';
  } else {
    return 'bg-red-800';
  }
}

function renderStatusText(statusCode) {
  if (statusCode == 200) {
    return "sesam ready"
  } else {
    return "server offline, please be patient"
  }
}

async function handleClick() {
  const status = await makeRequest();
  if (status == 200) {
    store.serverOnline.set(true);
  } else {
    store.serverOnline.set(false);
  }

}

handleClick()
</script>

<section class="flex text-sm font-thin gap-2">
  <span class="h-6 w-6 rounded-full {renderStatusIconColor(statusCode)}" on:click={handleClick}></span>
  <p>{renderStatusText(statusCode)}</p>
</section>
