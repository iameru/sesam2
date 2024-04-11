<script>
import DoorButtons from './lib/DoorButtons.svelte';
import store from './store/store.ts';

// doors we have access to here
const doorsMock = [
  {
    id: '2qwe2',
    name: 'door wonder'
  },
  {
    id: '123az',
    name: 'door something'
  },
]


</script>

<DoorButtons doors={doorsMock} />
