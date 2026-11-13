(() => {
  const image = document.getElementById("story-image");

  function renderStatus(data) {
    if (!data || !data.status || !data.image) return;

    // Evita piscar a tela se o servidor reenviar o mesmo estado.
    if (image.dataset.status !== data.status) {
      image.src = data.image;
      image.dataset.status = data.status;
    }
  }

  // EventSource mantém uma conexão aberta. O servidor avisa quando o status muda;
  // a página troca apenas a imagem, sem reload/refresh.
  const events = new EventSource("/api/events");
  events.addEventListener("status", (event) => {
    try {
      renderStatus(JSON.parse(event.data));
    } catch (error) {
      console.error("Não foi possível interpretar a atualização de status.", error);
    }
  });

  events.onerror = () => {
    // O EventSource tenta reconectar automaticamente se a conexão cair.
    console.warn("Conexão em tempo real interrompida; tentando reconectar...");
  };
})();
