document.addEventListener('DOMContentLoaded', function() {
  const button = document.getElementById('algumId');
  if (button) {
      button.addEventListener('click', function() {
          console.log('Botão clicado!');
      });
  } else {
      console.warn('Elemento com ID "algumId" não encontrado!');
  }
});
