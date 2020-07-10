(() => {
  const modelDropzone = document.getElementById('model-dropzone')
  const modelFile = document.getElementById('model-file')
  const modelSend = document.getElementById('model-send')
  const modelEmail = document.getElementById('model-email')
  const modelFormats = document.getElementById('model-formats')
  const modelFileName = document.getElementById('model-file-name')
  const modal = document.getElementById('modal')
  const modalIcon = modal.querySelector('.modal__icon')
  const modalMessage = modal.querySelector('.modal__message')
  const modalClose = modal.querySelector('.modal__close')
  const modalLoader = modal.querySelector('.modal__loader')
  let fileToUpload;

  ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    modelDropzone.addEventListener(eventName, evt => {
      evt.preventDefault()
      evt.stopPropagation()
    })
  })

  ;['dragenter', 'dragover'].forEach(eventName => {
    modelDropzone.addEventListener(eventName, evt => {
      modelDropzone.classList.add('model__dropzone--highlight')
    })
  })

  ;['dragleave', 'drop'].forEach(eventName => {
    modelDropzone.addEventListener(eventName, evt => {
      modelDropzone.classList.remove('model__dropzone--highlight')
    })
  })

  modelDropzone.addEventListener('drop', evt => {
    fileToUpload = evt.dataTransfer.files[0]

    if (fileToUpload == null) {
      modelFileName.innerText = ''
      modelFileName.classList.remove('model__file__name--visible')
      return
    }

    modelFileName.innerText = `Arquivo selecionado: ${fileToUpload.name}`
    modelFileName.classList.add('model__file__name--visible')
  })

  modelFile.addEventListener('change', evt => {
    fileToUpload = evt.target.files[0]

    if (fileToUpload == null) {
      modelFileName.innerText = ''
      modelFileName.classList.remove('model__file__name--visible')
      return
    }

    modelFileName.innerText = `Arquivo selecionado: ${fileToUpload.name}`
    modelFileName.classList.add('model__file__name--visible')
  })

  modelSend.addEventListener('click', async (evt) => {
    const url = 'https://upload-file-dot-epidemicapp-280600.rj.r.appspot.com/upload_file'
    const formData = new FormData()

    const selectedFormat = Array.from(modelFormats.querySelectorAll('input[type=radio]'))
      .filter(format => format.checked)[0]

    if (fileToUpload == null || modelEmail.value == '' || selectedFormat == null) {
      modalIcon.innerHTML = '&xotime;'
      modalIcon.classList.add('modal__icon--fail')
      modalMessage.innerText = 'Preencha todos os campos antes de enviar.'
      modal.classList.add('modal--raise')
      return
    }

    formData.append('file', fileToUpload)
    formData.append('email', modelEmail.value)
    formData.append('output', selectedFormat.value)

    try {
      modal.classList.add('modal--raise')
      modalLoader.classList.add('modal__loader--visible')

      await httpRequest(url, 'POST', formData)

      modalLoader.classList.remove('modal__loader--visible')
      modalIcon.innerHTML = '&check;'
      modalIcon.classList.add('modal__icon--success')
      modalMessage.innerText = 'Tudo certo! Seu modelo já está sendo gerado. Aguarde nosso email!'
      modelEmail.value = ''
      modelFile.value = ''
      modelFileName.innerText = ''
      modelFileName.classList.remove('model__file__name--visible')
      modelFormats.querySelector('input[type=radio]').checked = true
    } catch (err) {
      console.error(err, err.data)
      const errorMessage = err.data != null ? err.data.erro : 'Erro não informado.'
      modalLoader.classList.remove('modal__loader--visible')
      modalIcon.innerHTML = '&xotime;'
      modalIcon.classList.add('modal__icon--fail')
      modalMessage.innerText = `Oops! O seguinte erro ocorreu durante a requisição: ${errorMessage}`
      modal.classList.add('modal--raise')
    }
  })

  modalClose.addEventListener('click', evt => {
    modal.classList.remove('modal--raise')
    modalIcon.innerHTML = ''
    modalIcon.classList.remove('modal__icon--success', 'modal__icon--fail')
    modalMessage.innerText = ''
  })

  function httpRequest(url, method, data) {
    return fetch(url, {
      method: method,
      body: (data instanceof FormData) ? data : JSON.stringify(data),
      headers: (data instanceof FormData) ? {} : { 'Content-Type': 'application/json' }
    }).then(response => {
      if (response.ok) return response
      return response.json().then(errData => {
        const error = new Error('Something went wrong with your request. Check error data.')
        error.data = errData
        throw error
      })
    })
  }
})()
