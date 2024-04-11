<script>
export let doors

function buttonPush(buttonId) {
  // we want to make the correct request here and generate feedback about the call for the user.
  console.log(buttonId)
}
</script>

<section id='door-buttons' class='flex flex-col gap-10'>
  {#each [...doors] as door}
    <button
      class='w-40 h-40 bg-yellow-900 border border-black shadow-md text-zinc-950 shadow-black rounded-2xl touch-pan-up hover:font-medium hover:translate-x-1 hover:rotate-1 hover:bg-yellow-950 focus:bg-lime-950'
      on:click={buttonPush(door.id)}
    >{door.name}</button>
  {/each}
</section>
