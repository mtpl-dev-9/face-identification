// JS for live attendance page
document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const statusDiv = document.getElementById("live-status");
  const attendanceList = document.getElementById("attendanceList");

  // Only run on live attendance page
  if (video && canvas && attendanceList) {
    // start camera
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        video.srcObject = stream;
      })
      .catch(err => {
        if (statusDiv) {
          statusDiv.innerHTML = "<span class='text-danger'>Camera access denied: " + err + "</span>";
        }
      });

    // periodically capture frame and send to backend
    const sendFrame = () => {
      if (video.readyState !== video.HAVE_ENOUGH_DATA) {
        return;
      }
      const w = video.videoWidth;
      const h = video.videoHeight;
      if (!w || !h) return;

      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, w, h);

      const dataURL = canvas.toDataURL("image/jpeg");

      fetch("/api/attendance/live-mark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataURL })
      })
      .then(res => res.json())
      .then(data => {
        if (!statusDiv) return;
        if (data.match) {
          statusDiv.innerHTML = `<span class="text-success">Recognized: ${data.person.name} (${data.person.employee_code}) at ${data.attendance.timestamp}</span>`;
        } else {
          statusDiv.innerHTML = `<span class="text-muted">${data.message || "No match"}</span>`;
        }
        loadAttendance();
      })
      .catch(err => {
        if (statusDiv) {
          statusDiv.innerHTML = `<span class="text-danger">Error: ${err}</span>`;
        }
      });
    };

    setInterval(sendFrame, 4000); // every 4 seconds

    function loadAttendance() {
      fetch("/api/attendance/latest")
        .then(res => res.json())
        .then(data => {
          attendanceList.innerHTML = "";
          if (!data.results) return;
          data.results.forEach(item => {
            const li = document.createElement("li");
            li.className = "list-group-item";
            li.innerHTML = `
              <strong>${item.person_name || "-"}</strong>
              <span class="text-muted"> (${item.employee_code || "-"})</span><br>
              <small>${item.timestamp}</small>
              <span class="badge bg-secondary ms-2">${item.source}</span>
            `;
            attendanceList.appendChild(li);
          });
        });
    }

    loadAttendance();
    setInterval(loadAttendance, 10000);
  }
});
