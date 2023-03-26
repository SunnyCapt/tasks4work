const urlInput = document.querySelector('#url')
const resultDiv = document.querySelector('#result')

let checkUrlTimeoutId
let renderResultTimeoutId

function renderResult(msg, timeout=0) {
  if (!!timeout) {
    resultDiv.innerHTML = msg
    return
  }

  renderResultTimeoutId = setTimeout(() => {
    resultDiv.innerHTML = msg
  }, timeout)
}

urlInput.addEventListener('input', async (event) => {
  clearTimeout(renderResultTimeoutId)
  clearTimeout(checkUrlTimeoutId)

  resultDiv.innerHTML = ''

  checkUrlTimeoutId = setTimeout(async () => {
    try {
      await checkUrl(event.target.value)
    } catch (error) {
      console.error(error)
    }
  }, 1000)
})

async function callCheckUrlEndpoint(url) {
  const data = [
      {"is_exists": true, "type": "file"},
      {"is_exists": true, "type": "directory"},
      {"is_exists": false}
  ]
  return data[Math.ceil(Math.random() * data.length)]
}

async function checkUrl(url) {
  if (!url) {
    renderResult('')
    return
  }

  const regex = /^(https?|ftp):\/\/[^\s/$.?#].[^\s]*$/i
  if (!regex.test(url)) {
    renderResult('Invalid URL format.', 500)
    return
  }

  try {
    let respone = await callCheckUrlEndpoint(url)
    let result = `${respone.is_exists?'exists':'does not exist'}`
    if (!!respone.type)
      result = `the ${respone.type} ${result}`
    renderResult(result, 500)
  } catch (error) {
    console.error(error)
    renderResult('Try again...', 500)
  }
}
