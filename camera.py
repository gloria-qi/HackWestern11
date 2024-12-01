import cv2

def open_camera():
# Initialize the camera
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Error: Could not access the camera.")
        exit()

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = cam.read()

        if not success:
            print("Warning: Failed to capture frame. Retrying...")
            continue

        # Display the frame
        cv2.imshow('Camera', frame)

        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cam.release()
    cv2.destroyAllWindows()