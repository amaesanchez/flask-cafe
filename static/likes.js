"use strict";



const $likeBtn = $('#like-unlike')

async function updateLikedCafes(evt) {
  evt.preventDefault();
  const cafe_id = $(evt.target).attr('name');

  const likesBool = await getLikeStatus(cafe_id)

  if (likesBool) {
    const unliked = await unlikeCafe(cafe_id)
    return unliked

  } else {
    const liked = await likeCafe(cafe_id)
    return liked
  }
}

async function getLikeStatus(cafe_id) {
  const resp = await axios.get('/api/likes', {params:
    {"cafe_id" : cafe_id}
  });

  console.log(resp.data)

  return resp.data.likes
}

async function likeCafe(cafe_id) {
  //post to api/likes
  console.debug('like')

  const resp = await axios({
    url : '/api/likes',
    method : 'POST',
    data : {
      "cafe_id" : cafe_id
    }
  });

  console.debug(resp.data)

  fillLike()
}

function fillLike() {
  $likeBtn.removeClass('btn-outline-primary').addClass('btn-primary')
}

async function unlikeCafe(cafe_id) {
  //post to api/unlike
  console.debug("unlike")

  const resp = await axios({
    url : '/api/unlike',
    method : 'POST',
    data : {
      "cafe_id" : cafe_id
    }
  });

  console.debug(resp.data)

  unfillLike()
}

function unfillLike() {
  $likeBtn.removeClass('btn-primary').addClass('btn-outline-primary')
}

$likeBtn.on('click', updateLikedCafes)


