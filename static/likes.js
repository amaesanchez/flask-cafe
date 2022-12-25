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

  return resp.data.likes
}

async function likeCafe(cafe_id) {
  //post to api/likes
  console.log('like')

  const resp = await axios({
    url : '/api/likes',
    method : 'POST',
    data : {
      "cafe_id" : cafe_id
    }
  });

  return resp.data
}

async function unlikeCafe(cafe_id) {
  //post to api/unlike
  console.log("unlike")
  const resp = await axios({
    url : '/api/unlike',
    method : 'POST',
    data : {
      "cafe_id" : cafe_id
    }
  });

  return resp.data;
}

$likeBtn.on('click', updateLikedCafes)
