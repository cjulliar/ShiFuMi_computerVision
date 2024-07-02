const overlay = document.createElement('canvas');
const view = overlay.transferControlToOffscreen();

(async () => {
  // Create a PixiJS application.
  const app = new PIXI.Application();
  // Intialize the application.
  await app.init({ view, background: '#1099bb', resizeTo: window });
  document.body.appendChild(app.canvas);

  const container = new PIXI.Container();
  app.stage.addChild(container);
})()