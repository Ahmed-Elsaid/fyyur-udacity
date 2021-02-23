///////////////////////////////////////////////////////////
/////////////// Global Variables /////////////////////////
/////////////////////////////////////////////////////////

const fields = document.querySelectorAll('.form-control')
const newVenue = document.getElementById('new_venue')
const newArtist = document.getElementById('new_artist')
const newShow = document.getElementById('new_show')
const editVenue = document.getElementById('edit_venue')
const editArtist = document.getElementById('edit_artist')
const deleteVenue = document.getElementById('venue_delete')
const deleteArtist = document.getElementById('artist_delete')
const feedback = document.getElementById('feedback')
const feedbackMsg = document.getElementById('feedback_msg')

///////////////////////////////////////////////////////////
/////////////// Helper Functions /////////////////////////
/////////////////////////////////////////////////////////

// Extract the fields data 
const extractFieldsData = _ => {
  const fieldData = {}
  fields.forEach(field => {
    const newValue = field.value
    const name = field.name
    if(name === 'genres'){
      const genres = []
      const options = [...field.options]
      options.forEach(option => {
        if(option.selected === true){
          genres.push(option.value)
        }
      })
      fieldData[name] = genres
    }else if(name == 'seeking_venue' || name == 'seeking_talent'){
      if(field.checked) fieldData[name] = newValue == 'Yes' ? true : false
    }else if(name == 'songs'){
      if(newValue) fieldData[name] = newValue.split(',')
      else fieldData[name] = null
    }else {
      fieldData[name] = newValue
    }
  })
  return fieldData
}
// Display the success or error message to the user
const showFeedbackMsg = (varient, msg) => { 
  feedbackMsg.innerHTML = msg
  if (varient == 'error'){
    feedback.classList.remove('success')
    feedback.classList.add('error')
  }else{
    feedback.classList.remove('error')
    feedback.classList.add('success')
  }

  setTimeout(() => {
    feedback.classList.remove('error')
    feedback.classList.remove('success')
  },3000)
}

// send fileds data to the server for processing
const apiServices = async (data = {}, url = '',method = 'POST') => {
  return await fetch(url,{
    method,
    credentials:'same-origin',
    headers:{
      'content-type':'application/json'
    },
    body:JSON.stringify(data)
  })
}

// pass the fields data to apiServices function and handle the response from the server
const handleFieldData = async (url = '') => {
  const data = extractFieldsData()
  console.log(data)
  try {
    const response = await apiServices(data, url)
    const response_data = await response.json()
    showFeedbackMsg('success', response_data.message)
  } catch (error) {
    showFeedbackMsg('error',error)
  }
}

const redirect = (url) => {
  setTimeout(() => {
    window.location.href = url
  },3500)
}

///////////////////////////////////////////////////////////
/////////////// main Functions /////////////////////////
/////////////////////////////////////////////////////////

newVenue && newVenue.addEventListener('submit',async (e) => {
  e.preventDefault()
  handleFieldData('/venues/create')
  redirect('/venues')
})

newArtist && newArtist.addEventListener('submit', async (e) => {
  e.preventDefault()
  handleFieldData('/artists/create')
  redirect('/artists')
})

newShow && newShow.addEventListener('submit', async(e) => {
  e.preventDefault()
  handleFieldData('/shows/create')
  redirect('/shows')
})

editVenue && editVenue.addEventListener('submit', async (e) => {
  e.preventDefault()
  url = window.location.pathname
  id = url.split('/')[2]
  handleFieldData(url)
  redirect(`/venues/${id}`)
})

editArtist && editArtist.addEventListener('submit', async (e) => {
  e.preventDefault()
  url = window.location.pathname
  id = url.split('/')[2]
  handleFieldData(url)
  redirect(`/artists/${id}`)
})



deleteVenue && deleteVenue.addEventListener('click', async (e) => {
  const id = deleteVenue.dataset.id
  const url = `/venues/${id}`
  try {
    const response = await apiServices({}, url,'DELETE')
    const response_data = await response.json()
    showFeedbackMsg('success', response_data.message)
    redirect('/venues')
  } catch (error) {
    showFeedbackMsg('error',error)
  }
})

deleteArtist && deleteArtist.addEventListener('click', async (e) => {
  const id = deleteArtist.dataset.id
  const url = `/artists/${id}`
  try {
    const response = await apiServices({}, url,'DELETE')
    const response_data = await response.json()
    showFeedbackMsg('success', response_data.message)
    redirect('/artists')
  } catch (error) {
    showFeedbackMsg('error',error)
  }
})

tagger(document.querySelector('[name="songs"]'));

window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};