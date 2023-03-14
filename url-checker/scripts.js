const urlInput = document.querySelector('#url');
const resultDiv = document.querySelector('#result');

let timeoutId;

urlInput.addEventListener('input', async (event) => {
  clearTimeout(timeoutId);
  const inputValue = event.target.value;
  timeoutId = setTimeout(async () => {
    try {
      await checkUrl(inputValue);
    } catch (error) {
      console.error(error);
    }
  }, 1000);
});

async function checkUrl(url) {
  let result;

  if (!url) {
    resultDiv.innerHTML = '';
    return;
  }

  const regex = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i;
  if (!regex.test(url)) {
    resultDiv.innerHTML = 'Invalid URL format.';
    return;
  }

  try {
    const response = await fetch(`/check?url=${url}`);
    const data = await response.json();
    console.log(data);
    result = `${data.is_exists?'exists':'does not exist'}`
    if (!!data.is_exists && !!data.type)
      result = `the ${data.type} ${result}`;
  } catch (error) {
    console.error(error);
    result = 'Internal error';
  }

  setTimeout(() => {
    resultDiv.innerHTML = result;
  }, 500);
}
