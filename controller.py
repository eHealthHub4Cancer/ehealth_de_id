import wx
import os
import logging
import base64
import subprocess
from crypt4gh.lib import encrypt, decrypt
from crypt4gh.keys import get_private_key, get_public_key
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.Show()

        # Bind events
        self.view.Bind(wx.EVT_RADIOBUTTON, self.on_mode_change, self.view.radio_generate_id)
        self.view.Bind(wx.EVT_RADIOBUTTON, self.on_mode_change, self.view.radio_encrypt)
        self.view.Bind(wx.EVT_RADIOBUTTON, self.on_mode_change, self.view.radio_generate_keys)
        self.view.Bind(wx.EVT_BUTTON, self.on_generate_ids, self.view.generate_id_btn)
        self.view.Bind(wx.EVT_BUTTON, self.on_process, self.view.process_btn)
        self.view.Bind(wx.EVT_BUTTON, self.on_generate_keys, self.view.generate_keys_btn)

        # Timer for async generation
        self.timer = wx.Timer(self.view)
        self.view.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

        # Generation state
        self.ids = []
        self.num_ids = 0
        self.dest_path = ""
        self.file_type = ""
        self.batch_size = 100
        self.current_batch = 0
        self.num_batches = 0
        self.progress_dialog = None
        self.start_counter = 0

        # Initial state
        self.view.radio_generate_id.SetValue(True)
        self.on_mode_change(None)

    def on_mode_change(self, event):
        if self.view.radio_generate_id.GetValue():
            self.view.switch_panel(self.view.generate_id_panel)
        elif self.view.radio_encrypt.GetValue():
            self.view.switch_panel(self.view.encrypt_panel)
        elif self.view.radio_generate_keys.GetValue():
            self.view.switch_panel(self.view.generate_keys_panel)

    def on_generate_ids(self, event):
        seed = self.view.get_seed()
        num_ids = self.view.get_num_ids()
        dest_path = self.view.get_dest_path()
        file_type = self.view.get_file_type()

        if not num_ids.isdigit() or int(num_ids) <= 0:
            self.view.show_message("Please enter a valid number of IDs.", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not dest_path:
            self.view.show_message("Please specify a destination directory.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Initialize generation state
        self.num_ids = int(num_ids)
        self.dest_path = dest_path
        self.file_type = file_type
        self.model.set_seed(seed)
        self.ids = []
        self.current_batch = 0
        self.num_batches = (self.num_ids + self.batch_size - 1) // self.batch_size  # Ceiling division
        self.start_counter = 0

        # Initialize progress dialog
        self.progress_dialog = wx.ProgressDialog(
            "Generating IDs",
            "Processing...",
            maximum=self.num_batches,
            parent=self.view,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT
        )

        # Start the timer to process batches
        self.timer.Start(50)  # Update every 50ms

    def on_timer(self, event):
        if self.current_batch >= self.num_batches:
            # Generation complete
            self.timer.Stop()
            self.progress_dialog.Destroy()
            try:
                output_path = self.model.save_ids(self.ids, self.dest_path, self.file_type)
                self.view.show_message(f"Generated {len(self.ids)} IDs and saved to {output_path}.", "Success", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                self.view.show_message(str(e), "Error", wx.OK | wx.ICON_ERROR)
            return

        # Check if the user cancelled the operation
        keep_going, _ = self.progress_dialog.Update(self.current_batch, f"Generating batch {self.current_batch + 1} of {self.num_batches}")
        if not keep_going:
            self.timer.Stop()
            self.progress_dialog.Destroy()
            self.view.show_message("ID generation cancelled.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        # Generate a batch of IDs
        batch_count = min(self.batch_size, self.num_ids - len(self.ids))
        batch_ids = self.model.generate_ids(batch_count, self.start_counter)
        self.ids.extend(batch_ids)
        self.start_counter += batch_count
        self.current_batch += 1

    def on_process(self, event):
        file_path = self.view.get_file_path()
        key_path = self.view.get_key_path()
        action = self.view.get_encrypt_action()

        if not file_path or not key_path:
            self.view.show_message("Please select both a file and a key.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Check if input file exists and is readable
        if not os.path.isfile(file_path):
            self.view.show_message(f"Input file {file_path} does not exist.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Determine output file path (append .c4gh for encryption, original name for decryption)
        output_file = file_path + ".c4gh" if action == "Encrypt" else os.path.splitext(file_path)[0]

        # Check if output file can be written
        if os.path.exists(output_file):
            self.view.show_message(f"Output file {output_file} already exists. Please remove it or choose a different input file.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Prompt for passphrase if decrypting with an encrypted private key
        passphrase = None
        if action == "Decrypt":
            passphrase_dialog = wx.TextEntryDialog(
                self.view,
                "Enter passphrase for the private key (if encrypted):",
                "Passphrase for Private Key",
                "",
                style=wx.TE_PASSWORD | wx.OK | wx.CANCEL
            )
            if passphrase_dialog.ShowModal() == wx.ID_OK:
                passphrase = passphrase_dialog.GetValue().encode() if passphrase_dialog.GetValue() else None
            else:
                passphrase_dialog.Destroy()
                self.view.show_message("Decryption cancelled.", "Info", wx.OK | wx.ICON_INFORMATION)
                return
            passphrase_dialog.Destroy()

        try:
            with open(file_path, 'rb') as f_in, open(output_file, 'wb') as f_out:
                if action == "Encrypt":
                    # Load and validate recipient's public key
                    try:
                        public_key = get_public_key(key_path)
                        logger.debug(f"Public key object: {public_key}, Type: {type(public_key)}")
                        # Log key file contents
                        with open(key_path, 'r') as f:
                            key_content = f.read()
                            logger.debug(f"Public key file content:\n{key_content}")
                        # Attempt to extract raw key bytes
                        raw_bytes = None
                        try:
                            if isinstance(public_key, bytes):
                                raw_bytes = public_key
                                logger.debug(f"Public key is raw bytes: {base64.b64encode(raw_bytes).decode('utf-8')}")
                            else:
                                raw_bytes = public_key.public_bytes(
                                    encoding=serialization.Encoding.Raw,
                                    format=serialization.PublicFormat.Raw
                                )
                                logger.debug(f"Public key raw bytes: {base64.b64encode(raw_bytes).decode('utf-8')}")
                        except AttributeError:
                            logger.debug("Public key object does not support public_bytes")
                    except Exception as e:
                        raise ValueError(f"Failed to load public key: {str(e)}")
                    if not public_key:
                        raise ValueError("Public key is None or invalid.")
                    # Try encryption with both key object and raw bytes
                    key_attempts = [(0, public_key)]
                    if raw_bytes:
                        key_attempts.append((0, raw_bytes))
                    for attempt_key in key_attempts:
                        try:
                            logger.debug(f"Encrypting with key tuple: {attempt_key}")
                            encrypt(
                                [attempt_key],  # Try method 0 (X25519)
                                None,  # No sender private key
                                f_in,
                                f_out
                            )
                            self.view.show_message(f"Encrypted {os.path.basename(file_path)} to {os.path.basename(output_file)}.", "Success", wx.OK | wx.ICON_INFORMATION)
                            break
                        except Exception as e:
                            logger.error(f"Encryption failed with key {attempt_key}: {str(e)}")
                            if attempt_key == key_attempts[-1]:
                                raise ValueError(f"All encryption attempts failed: {str(e)}")
                elif action == "Decrypt":
                    # Load and validate user's private key
                    try:
                        private_key = get_private_key(key_path, lambda: passphrase)
                        logger.debug(f"Private key object: {private_key}, Type: {type(private_key)}")
                    except Exception as e:
                        raise ValueError(f"Failed to load private key: {str(e)}")
                    if not private_key:
                        raise ValueError("Private key is None or invalid.")
                    # Decrypt the file
                    logger.debug(f"Decrypting with key tuple: [(0, {private_key})]")
                    decrypt(
                        [(0, private_key)],  # Method 0 (X25519)
                        None,  # No sender public key
                        f_in,
                        f_out
                    )
                    self.view.show_message(f"Decrypted {os.path.basename(file_path)} to {os.path.basename(output_file)}.", "Success", wx.OK | wx.ICON_INFORMATION)
        except ValueError as ve:
            self.view.show_message(f"Validation error: {str(ve)}", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            self.view.show_message(f"Failed to {action.lower()} file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

    def on_generate_keys(self, event):
        logger.debug("Starting key generation")
        output_dir = self.view.get_key_output_path()
        if not output_dir:
            logger.debug("No output directory selected")
            self.view.show_message("Please select an output directory.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Check if output directory exists and is writable
        if not os.path.isdir(output_dir) or not os.access(output_dir, os.W_OK):
            logger.debug(f"Output directory {output_dir} is invalid or not writable")
            self.view.show_message(f"Output directory {output_dir} is invalid or not writable.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Prompt for key name
        logger.debug("Prompting for key name")
        key_name_dialog = wx.TextEntryDialog(
            self.view,
            "Enter a name for the key pair:",
            "Key Name",
            "",
            style=wx.OK | wx.CANCEL
        )
        if key_name_dialog.ShowModal() != wx.ID_OK:
            logger.debug("Key name dialog cancelled")
            key_name_dialog.Destroy()
            self.view.show_message("Key generation cancelled.", "Info", wx.OK | wx.ICON_INFORMATION)
            return
        key_name = key_name_dialog.GetValue().strip()
        key_name_dialog.Destroy()
        logger.debug(f"Key name entered: {key_name}")

        # Validate key name
        if not key_name or not all(c.isalnum() or c == '_' for c in key_name):
            logger.debug("Invalid key name")
            self.view.show_message("Key name must be non-empty and contain only alphanumeric characters or underscores.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Define paths for private and public keys using the key name
        private_key_path = os.path.join(output_dir, f"{key_name}_private.sec")
        public_key_path = os.path.join(output_dir, f"{key_name}_public.pub")
        logger.debug(f"Private key path: {private_key_path}")
        logger.debug(f"Public key path: {public_key_path}")

        # Check if keys already exist
        for key_path in (private_key_path, public_key_path):
            if os.path.isfile(key_path):
                logger.debug(f"Key file already exists: {key_path}")
                self.view.show_message(f"Key {key_path} already exists. Please remove it or choose a different name.", "Error", wx.OK | wx.ICON_ERROR)
                return

        # Prompt for passphrase
        logger.debug("Prompting for passphrase")
        passphrase_dialog = wx.TextEntryDialog(
            self.view,
            "Enter passphrase for the private key (leave empty for no passphrase):",
            "Passphrase for Private Key",
            "",
            style=wx.TE_PASSWORD | wx.OK | wx.CANCEL
        )
        if passphrase_dialog.ShowModal() != wx.ID_OK:
            logger.debug("Passphrase dialog cancelled")
            passphrase_dialog.Destroy()
            self.view.show_message("Key generation cancelled.", "Info", wx.OK | wx.ICON_INFORMATION)
            return

        passphrase = passphrase_dialog.GetValue().encode() if passphrase_dialog.GetValue() else None
        passphrase_dialog.Destroy()
        logger.debug(f"Passphrase provided: {'Yes' if passphrase else 'No'}")

        try:
            # Generate keys with crypt4gh-keygen
            logger.debug("Attempting key generation with crypt4gh-keygen")
            temp_private_key_path = os.path.join(output_dir, f"{key_name}_temp_private.sec")
            try:
                cmd = ["crypt4gh-keygen", "--sk", temp_private_key_path, "--pk", public_key_path]
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                logger.debug(f"crypt4gh-keygen output: {result.stdout}")

                # Read and log key file contents
                with open(public_key_path, 'r') as f:
                    public_content = f.read()
                    logger.debug(f"Public key file content:\n{public_content}")
                with open(temp_private_key_path, 'r') as f:
                    private_content = f.read()
                    logger.debug(f"Temporary private key file content:\n{private_content}")

                # Handle passphrase encryption for private key
                if passphrase:
                    logger.debug("Encrypting private key with passphrase using cryptography")
                    # Load the crypt4gh-generated private key
                    try:
                        temp_private_key = get_private_key(temp_private_key_path, lambda: None)
                        private_bytes = temp_private_key.private_bytes(
                            encoding=serialization.Encoding.Raw,
                            format=serialization.PrivateFormat.Raw
                        )
                        # Create a new private key object for encryption
                        private_key = x25519.X25519PrivateKey.from_private_bytes(private_bytes)
                        private_bytes_encrypted = private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.PKCS8,
                            encryption_algorithm=serialization.BestAvailableEncryption(passphrase)
                        )
                        private_content = private_bytes_encrypted.decode('utf-8')
                        with open(private_key_path, 'w') as f:
                            f.write(private_content)
                        logger.debug(f"Encrypted private key file content:\n{private_content}")
                    finally:
                        # Clean up temporary private key
                        if os.path.exists(temp_private_key_path):
                            os.remove(temp_private_key_path)
                            logger.debug("Removed temporary private key file")
                else:
                    # No passphrase, use the generated private key as-is
                    os.rename(temp_private_key_path, private_key_path)
                    with open(private_key_path, 'r') as f:
                        private_content = f.read()
                        logger.debug(f"Private key file content:\n{private_content}")

                # Validate public key
                logger.debug("Validating public key with crypt4gh")
                validated_public_key = get_public_key(public_key_path)
                if not validated_public_key:
                    logger.error("crypt4gh failed to load public key")
                    raise ValueError("crypt4gh failed to load public key")
                logger.debug(f"Public key object: {validated_public_key}, Type: {type(validated_public_key)}")
                try:
                    public_bytes = validated_public_key.public_bytes(
                        encoding=serialization.Encoding.Raw,
                        format=serialization.PublicFormat.Raw
                    )
                    logger.debug(f"Public key raw bytes: {base64.b64encode(public_bytes).decode('utf-8')}")
                except AttributeError:
                    logger.debug("Public key object does not support public_bytes")

            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"crypt4gh-keygen failed: {str(e)}")
                raise ValueError(f"Failed to generate keys with crypt4gh-keygen: {str(e)}")

            # Set secure file permissions
            logger.debug("Setting file permissions")
            os.chmod(private_key_path, 0o600)
            os.chmod(public_key_path, 0o644)

            logger.debug("Key generation and validation successful")
            self.view.show_message(
                f"Generated private key at {private_key_path} and public key at {public_key_path}.",
                "Success",
                wx.OK | wx.ICON_INFORMATION
            )

        except OSError as e:
            logger.error(f"OSError during key generation: {str(e)}")
            self.view.show_message(f"Failed to write keys: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
        except ValueError as e:
            logger.error(f"ValueError during key generation: {str(e)}")
            self.view.show_message(f"Key generation failed: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error during key generation: {str(e)}")
            self.view.show_message(f"Unexpected error: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)