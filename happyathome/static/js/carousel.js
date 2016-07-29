var Carousel = (function() {
    var Carousel = function() {
        this.fov = 75;
        this.savedX = 0;
        this.savedY = 0;
        this.longitude = 0;
        this.latitude = 0;
        this.savedLongitude = 0;
        this.savedLatitude = 0;
        this.autoFlow = true;
        this.isUserInteracting = false;
    }

    Carousel.prototype = {
        viewer: function(viewerId, options) {
            var like_icon = document.createElement("span"),
                scrap_icon = document.createElement("span"),
                share_icon = document.createElement("span"),
                content_like = document.createElement("div"),
                content_scrap = document.createElement("div"),
                content_share = document.createElement("div");

            like_icon.classList.add('like-icon');
            if (options.is_like) {
                like_icon.classList.add('active');
            }

            scrap_icon.classList.add('scrap-icon');
            if (options.is_scrap) {
                scrap_icon.classList.add('active');
            }
            share_icon.classList.add('share-icon');
            content_like.classList.add('content-like');
            content_like.appendChild(like_icon);
            content_scrap.appendChild(scrap_icon);
            content_scrap.classList.add('content-scrap');
            content_share.appendChild(share_icon);
            content_share.classList.add('content-share');

            this.photoWrap = document.getElementById(viewerId);
            this.photoWrap.style.position = "relative";
            if (options.action) {
                this.photoWrap.appendChild(content_like);
                this.photoWrap.appendChild(content_scrap);
                this.photoWrap.appendChild(content_share);
            }

            this.canvasWidth = this.photoWrap.offsetWidth;
            this.canvasHeight = this.photoWrap.offsetHeight;

            var sphere = new THREE.SphereGeometry(500, 60, 40);
            sphere.applyMatrix(new THREE.Matrix4().makeScale(-1, 1, 1));

            var loader = new THREE.TextureLoader();
            loader.crossOrigin = '';

            var sphereMaterial = new THREE.MeshBasicMaterial();
            sphereMaterial.map = loader.load(
                options.panorama,
                function (texture) {
                },
                function (xhr) {
                    console.log((xhr.loaded / xhr.total * 100) + '% loaded');
                },
                function (xhr) {
                    console.log('An error happened');
                }
            );

            this.scene = new THREE.Scene();
            this.scene.add(new THREE.Mesh(sphere, sphereMaterial));

            this.camera = new THREE.PerspectiveCamera(this.fov, this.canvasWidth / this.canvasHeight, 1, 1100);
            this.camera.target = new THREE.Vector3(0, 0, 0);

            this.renderer = new THREE.WebGLRenderer();
            this.renderer.setSize(this.canvasWidth, this.canvasHeight);

            this.photoWrap.appendChild(this.renderer.domElement);
            this.photoWrap.addEventListener("mouseup", this.onPhotoMouseUp.bind(this), false);

            this.photoWrap.addEventListener("mousedown", this.onPhotoMouseDown.bind(this), false);
            this.photoWrap.addEventListener("mousemove", this.onPhotoMouseMove.bind(this), false);
            this.photoWrap.addEventListener("mousewheel", this.onPhotoMouseWheel.bind(this), false);

            this.animate();
        },
        onPhotoMouseUp: function(event) {
            this.isUserInteracting = false;
        },
        onPhotoMouseDown: function(event) {
            event.preventDefault();

            this.autoFlow = false;
            this.isUserInteracting = true;

            this.savedX = event.clientX;
            this.savedY = event.clientY;

            this.savedLongitude = this.longitude;
            this.savedLatitude = this.latitude;
        },
        onPhotoMouseMove: function(event) {
            if (this.isUserInteracting) {
                this.longitude = (this.savedX - event.clientX) * 0.1 + this.savedLongitude;
                this.latitude = (event.clientY - this.savedY) * 0.1 + this.savedLatitude;
            }
        },
        onPhotoMouseWheel: function(event) {
            event.preventDefault();

            if (event.wheelDeltaY) {
                this.fov -= event.wheelDeltaY * 0.05;
            } else if (event.wheelDelta) {
                this.fov -= event.wheelDelta * 0.05;
            } else if (event.detail) {
                this.fov += event.detail * 1.0;
            }

            if (this.fov < 35) {
                this.fov = 35;
            } else if (this.fov > 95) {
                this.fov = 95;
            }

            this.camera.projectionMatrix.makePerspective(this.fov, this.canvasWidth / this.canvasHeight, 1, 1100);
            this.render();
        },
        animate: function() {
            this.render();
            window.requestAnimationFrame(this.animate.bind(this));
        },
        render: function() {
            if (this.autoFlow) {
                this.longitude += 0.07;
            }

            this.latitude = Math.max(-85, Math.min(85, this.latitude));

            this.camera.target.x = 500 * Math.sin(THREE.Math.degToRad(90 - this.latitude)) * Math.cos(THREE.Math.degToRad(this.longitude));
            this.camera.target.y = 500 * Math.cos(THREE.Math.degToRad(90 - this.latitude));
            this.camera.target.z = 500 * Math.sin(THREE.Math.degToRad(90 - this.latitude)) * Math.sin(THREE.Math.degToRad(this.longitude));
            this.camera.lookAt(this.camera.target);

            this.renderer.render(this.scene, this.camera);
        }
    };

    return Carousel;
})();
