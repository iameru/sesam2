<script>
let showAdminArea = false
function handleShowArea() {
  showAdminArea = !showAdminArea

}
</script>


<section class='flex flex-col gap-4'>
  <button
      class='px-4 py-2 bg-yellow-900 border border-black rounded-lg shadow-md text-zinc-950 shadow-black touch-pan-up hover:font-medium hover:translate-x-1 hover:rotate-1 hover:bg-yellow-950 focus:bg-lime-950'
    on:click={handleShowArea}
  >Admin Area</button>
  <section id='admin-area' class={showAdminArea ? "" : "hidden"}>
    Hi there!!!
  </section>
</section>
