/* Native fragment links work with or without JavaScript. */
const journey = document.querySelector('.journey');
if (journey) {
  const steps = [
    {
      title: 'Start with something that matters to you.',
      description: '“Help our book club choose its next book.” A small, real need is enough to begin. You shouldn’t have to start by understanding an entire platform.',
      takeaway: 'Your need is the starting point.',
      caption: 'A need connects to work already done.',
    },
    {
      title: 'Someone has already made a beginning.',
      description: 'One person made a reading list. Another made a voting tool. Imagine bringing those pieces together into something that fits your club, with a coding agent helping you make the connection.',
      takeaway: 'Cooperation through the things we make.',
      caption: 'Independent contributions become useful together.',
    },
    {
      title: 'Your answer can become someone else’s beginning.',
      description: 'Share the result. A film club could adapt it; another group could take it somewhere unexpected. The ambition is to make shared needs and the work that answers them visible, so people can choose where to help.',
      takeaway: 'Work builds on work. Possibilities multiply.',
      caption: 'An answer leaves room for the next possibility.',
    },
  ];
  const controls = journey.querySelector('.journey-steps');
  const buttons = [...controls.querySelectorAll('button')];
  const copy = journey.querySelector('.journey-copy');

  const selectStep = (index) => {
    if (journey.dataset.step === String(index)) return;
    const step = steps[index];
    journey.dataset.step = String(index);
    buttons.forEach((button, position) => {
      button.setAttribute('aria-pressed', String(position === index));
    });
    copy.querySelector('h3').textContent = step.title;
    copy.querySelector('.journey-description').textContent = step.description;
    copy.querySelector('.journey-takeaway').textContent = step.takeaway;
    journey.querySelector('.journey-caption').textContent = step.caption;
  };

  buttons.forEach((button, index) => {
    button.addEventListener('click', () => selectStep(index));
  });
  journey.classList.add('journey-ready');
  journey.dataset.step = '0';
  controls.hidden = false;
}
