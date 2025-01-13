import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import os
import subprocess

class WorkflowApp(tk.Tk):

    @staticmethod
    def windows_to_wsl_path(windows_path):
        """
        Convertit un chemin Windows en chemin compatible WSL.
        :param windows_path: Chemin Windows (par exemple : C:\\Users\\user\\Desktop\\file.su)
        :return: Chemin WSL correspondant (par exemple : /mnt/c/Users/user/Desktop/file.su)
        """
        if ":" in windows_path:
            drive, path = windows_path.split(":")
            wsl_path = f"/mnt/{drive.lower()}{path.replace('\\', '/')}"
            return wsl_path
        else:
            raise ValueError("Chemin Windows invalide.")

    def __init__(self):
        super().__init__()
        self.title("Sismique GUI")
        self.geometry("1024x768")

        self.output_dir = self.create_output_directory()

        self.modules = self.load_modules()
        self.workflow = []
        self.workflow_modules = set()
        self.stream = None
        self.corrected_stream = None
        self.stacked_stream = None

        self.create_menu()

        self.create_widgets()

    def create_output_directory(self):
        """
        Crée un répertoire spécifique sur le bureau pour stocker les fichiers de sortie.
        """
        user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        output_dir = os.path.join(user_desktop, "SeismicOutputs")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def create_menu(self):
        """
        Crée la barre de menu principale.
        """

        self.menu_bar = tk.Menu(self)

        self.menu_bar.add_cascade(label="    Documentation    ", menu=self.create_docu_menu())

        self.config(menu=self.menu_bar)


    def create_docu_menu(self):
        """
        Crée le menu Documentation avec les sections sous forme de sous-menus.
        """
        docu_menu = tk.Menu(self.menu_bar, tearoff=0)

        documentation_sections = [
            "Introduction",
            "Charger un fichier",
            "surange",
            "suvelan",
            "sunmo",
            "sustack",
            "suximage",
            "suxwigb",
        ]

        for section in documentation_sections:
            docu_menu.add_command(label=section, command=lambda sec=section: self.show_documentation_details(sec))

        return docu_menu

    def show_documentation_details(self, section):
        """
        Affiche les détails de la documentation pour une section sélectionnée.
        """
        detail_window = tk.Toplevel(self)
        detail_window.title(f"Documentation : {section}")
        detail_window.geometry("600x400")

        section_text = {
            "Introduction": "Bienvenue dans l'outil de traitement sismique. Cet outil vous permet de charger des fichiers SU et SEGY et d'éxecuter certaines commandes du logiciel SeismicUnix...",
            "Charger un fichier": "Pour charger un fichier SEGY, cliquez sur Projet > Charger un fichier...",
            "surange": "Get max and min values for non-zero header entries, command : surange <stdin",
            "suvelan": "Compute stacking velocity semblance for cdp gather, command : suvelan <stdin >stdout [optional parameters] Optional Parameters: nv=50 - number of velocities, dv=50.0 - velocity sampling interval, fv=1500.0 - first velocity",
            "sunmo": "NMO for an arbitrary velocity function of time and CDP, command : sunmo <stdin >stdout [optional parameters] Optional Parameters: tnmo=0,... - NMO times corresponding to velocities in vnmo, vnmo=1500,... - NMO velocities corresponding to times in tnmo",
            "sustack": "Stack adjacent traces having the same key header word, command : sustack <stdin >stdout",
            "suximage": "X-windows IMAGE plot of a segy data set, command : suxwimage <stdin",
            "suxwigb": "X-windows Bit-mapped wiggle plot of a segy data set, command : suxwigb <stdin",

        }

        detail_text = section_text.get(section, "Détails non disponibles pour cette section.")

        text_widget = tk.Text(detail_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, detail_text)
        text_widget.config(state=tk.DISABLED)

    def create_widgets(self):
        """
        éléments d'interface utilisateur pour les modules, le workflow et les résultats.
        """
        self.top_frame = ttk.Frame(self)
        self.top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.08)

        self.top_inner_frame = ttk.Frame(self.top_frame)
        self.top_inner_frame.pack(expand=True)

        self.load_button = ttk.Button(self.top_inner_frame, text="Charger un fichier", command=self.load_data)
        self.load_button.pack(side="left", padx=5)

        self.file_label = ttk.Label(self.top_inner_frame, text="Aucun fichier chargé", font=("Arial", 10, "italic"))
        self.file_label.pack(side="left", padx=5)

        self.module_frame = ttk.Frame(self)
        self.module_frame.place(relx=0.05, rely=0.1, relwidth=0.2, relheight=0.8)

        self.module_label = ttk.Label(self.module_frame, text="Modules disponibles")
        self.module_label.pack(pady=10)

        self.module_listbox = tk.Listbox(self.module_frame, font=("Arial", 11, "bold"), justify="center")
        self.module_listbox.pack(fill=tk.BOTH, expand=True)
        for module in self.modules:
            self.module_listbox.insert(tk.END, module["name"])

        self.module_listbox.bind("<Double-1>", self.on_module_double_click)

        self.workflow_frame = ttk.Frame(self)
        self.workflow_frame.place(relx=0.3, rely=0.1, relwidth=0.2, relheight=0.8)

        self.workflow_label = ttk.Label(self.workflow_frame, text="Workflow")
        self.workflow_label.pack(pady=10)

        self.workflow_listbox = tk.Listbox(self.workflow_frame, font=("Arial", 11, "bold"), justify="center")
        self.workflow_listbox.pack(fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self.workflow_frame)
        self.button_frame.pack(pady=10)

        self.run_icon = PhotoImage(file="resources/run.png")
        self.run_workflow_button = ttk.Button(self.workflow_frame, image=self.run_icon, compound="left", command=self.run_workflow)
        self.run_workflow_button.pack(side="left", padx=5, expand=True)


        self.add_icon = PhotoImage(file="resources/add.png")
        self.add_module_button = ttk.Button(self.workflow_frame, image=self.add_icon, compound="right", command=self.add_external_module)
        self.add_module_button.pack(side="left", padx=5, expand=True)

        self.result_frame = ttk.Frame(self)
        self.result_frame.place(relx=0.55, rely=0.1, relwidth=0.4, relheight=0.8)

        self.result_label = ttk.Label(self.result_frame, text="Résultats")
        self.result_label.pack(pady=10)

        self.result_text = tk.Text(self.result_frame)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.restart_icon = PhotoImage(file="resources/restart.png")
        self.restart_button = ttk.Button(self.result_frame, image=self.restart_icon, compound="left", command=self.close_project)
        self.restart_button.pack(pady=10)


    def load_modules(self):
        """
        Charge la liste des modules disponibles avec leurs fonctions associées.
        """
        modules = [
            {"name": "surange", "function": self.run_surange, "params": []},
            {"name": "suvelan", "function": self.run_suvelan, "params": ["nv", "dv", "fv"]},
            {"name": "suximage", "function": self.run_suximage, "params": []},
            {"name": "sunmo", "function": self.run_sunmo, "params": ["tnmo", "vnmo"]},
            {"name": "sustack", "function": self.run_sustack, "params": []},
            {"name": "suxwigb", "function": self.run_suxwigb, "params": []},
        ]
        return modules

    def load_data(self):
        """
        Ouvre une boîte de dialogue pour sélectionner et charger un fichier SEGY ou SU.
        """
        filepath = filedialog.askopenfilename(
            filetypes=[("SEGY Files", "*.sgy;*.segy"), ("SU Files", "*.su"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                if filepath.endswith(".su"):
                    self.su_file = filepath
                    self.result_text.insert(tk.END, f"Fichier SU chargé : {filepath}\n")
                    self.file_label.config(text=f"Fichier chargé : {os.path.basename(filepath)}")

                # Si c'est un fichier SEGY, effectuer la conversion
                elif filepath.endswith(".sgy") or filepath.endswith(".segy"):
                    output_su_file = os.path.join(self.output_dir, "output.su")

                    wsl_filepath = self.windows_to_wsl_path(filepath)
                    wsl_output_file = self.windows_to_wsl_path(output_su_file)

                    segyread_path = "/usr/local/cwp/bin/segyread"

                    command = f"wsl bash -c \"{segyread_path} tape={wsl_filepath} > {wsl_output_file}\""

                    process = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    stdout, stderr = process.communicate()

                    if process.returncode == 0:
                        self.su_file = output_su_file
                        self.result_text.insert(tk.END, f"Conversion SEG-Y -> SU réussie : {output_su_file}\n")
                        self.file_label.config(text=f"Fichier chargé : {os.path.basename(filepath)}")
                    else:
                        raise RuntimeError(f"Erreur dans segyread : {stderr}")

                else:
                    raise ValueError("Format de fichier non pris en charge.")

            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger le fichier : {e}")
        else:
            messagebox.showerror("Erreur", "Aucun fichier sélectionné.")


    def run_surange(self):
        """
        Exécute surange sur le fichier SU chargé et affiche les en-têtes dans le panneau de résultats.
        """
        try:
            su_file = getattr(self, "su_file", None)

            if not su_file:
                raise FileNotFoundError("Aucun fichier SU disponible pour surange.")

            wsl_su_file = self.windows_to_wsl_path(su_file)

            command = (
                f"wsl bash -c \"export CWPROOT=/usr/local/cwp; "
                f"/usr/local/cwp/bin/surange < {wsl_su_file}\""
            )

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")

            if process.returncode == 0:
                self.result_text.insert(tk.END, f"Résultats de surange :\n{stdout}\n")
            else:
                raise RuntimeError(f"Erreur dans surange : {stderr}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exécuter surange : {e}")



    def run_suvelan(self, nv, dv, fv):
        """
        Exécute suvelan sur le fichier SU chargé avec les paramètres spécifiés.
        Les résultats sont placés dans le répertoire de sortie.
        """
        if not hasattr(self, 'su_file') or not self.su_file:
            messagebox.showerror("Erreur", "Aucun fichier SU n'est chargé.")
            return

        try:
            wsl_su_file = self.windows_to_wsl_path(self.su_file)
            wsl_output_file = self.windows_to_wsl_path(os.path.join(self.output_dir, "output_suvelan.su"))
            print(f"Chemin WSL du fichier d'entrée : {wsl_su_file}")
            print(f"Chemin WSL du fichier de sortie : {wsl_output_file}")

            suvelan_path = "/usr/local/cwp/bin/suvelan"

            command = f"wsl bash -c \"{suvelan_path} < {wsl_su_file} nv={nv} dv={dv} fv={fv} > {wsl_output_file}\""
            print(f"Running command: {command}")

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")

            if process.returncode == 0:
                self.result_text.insert(tk.END, f"suvelan exécuté avec succès.\n")
                self.result_text.insert(tk.END, f"Fichier de sortie : {os.path.join(self.output_dir, 'output_suvelan.su')}\n")
                self.suvelan_output_file = os.path.join(self.output_dir, "output_suvelan.su")
            else:
                raise RuntimeError(f"Erreur dans suvelan : {stderr}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exécuter suvelan : {e}")

    def run_sunmo(self, tnmo, vnmo):
        """
        Exécute sunmo sur le fichier SU chargé avec les paramètres tnmo et vnmo.
        - Utilise l'output de suvelan s'il est dans le workflow.
        - Sinon, utilise le fichier SU chargé.
        """
        try:
            su_file = None

            for step in self.workflow:
                if step["module"]["name"] == "suvelan":
                    su_file = getattr(self, "suvelan_output_file", None)

            if not su_file:
                su_file = getattr(self, "su_file", None)

            if not su_file:
                raise FileNotFoundError("Aucun fichier SU disponible pour sunmo.")

            wsl_su_file = self.windows_to_wsl_path(su_file)
            wsl_output_file = self.windows_to_wsl_path(os.path.join(self.output_dir, "output_sunmo.su"))

            tnmo_str = ",".join(map(str, tnmo))
            vnmo_str = ",".join(map(str, vnmo))
            command = (
                f"wsl bash -c \"/usr/local/cwp/bin/sunmo < {wsl_su_file} tnmo={tnmo_str} vnmo={vnmo_str} > {wsl_output_file}\""
            )

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")

            if process.returncode == 0:
                self.result_text.insert(tk.END, f"sunmo exécuté avec succès.\n")
                self.result_text.insert(tk.END, f"Fichier de sortie : {os.path.join(self.output_dir, 'output_sunmo.su')}\n")
            else:
                raise RuntimeError(f"Erreur dans sunmo : {stderr}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exécuter sunmo : {e}")

    def run_sustack(self):
        """
        Exécute sustack sur le fichier SU chargé ou corrigé avec sunmo et affiche les résultats dans le panneau de résultats.
        """
        try:
            su_file = None

            for step in self.workflow:
                if step["module"]["name"] == "sunmo":
                    su_file = getattr(self, "sunmo_output_file", None)

            if not su_file:
                su_file = getattr(self, "su_file", None)

            if not su_file:
                raise FileNotFoundError("Aucun fichier SU disponible pour sustack.")

            wsl_su_file = self.windows_to_wsl_path(su_file)
            wsl_output_file = self.windows_to_wsl_path(os.path.join(self.output_dir, "output_sustack.su"))

            command = (
                f"wsl bash -c \"/usr/local/cwp/bin/sustack < {wsl_su_file} > {wsl_output_file}\""
            )

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")

            if process.returncode == 0:
                self.result_text.insert(tk.END, f"sustack exécuté avec succès.\n")
                self.result_text.insert(tk.END, f"Fichier de sortie : {os.path.join(self.output_dir, 'output_sustack.su')}\n")
                self.sustack_output_file = os.path.join(self.output_dir, "output_sustack.su")
            else:
                raise RuntimeError(f"Erreur dans sustack : {stderr}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exécuter sustack : {e}")


    def run_suxwigb(self):
        """
        Exécute suwigb pour afficher un fichier SU sous forme de wiggle plot.
        - Si sustack ou sunmo est exécuté avant, utilise leur fichier de sortie.
        - Sinon, affiche le fichier chargé via load_data.
        """
        try:
            su_file = None

            for step in reversed(self.workflow):
                if step["module"]["name"] in ["sustack", "sunmo","suvelan"]:
                    su_file = getattr(self, f"{step['module']['name']}_output_file", None)
                    break

            if not su_file:
                su_file = getattr(self, "su_file", None)

            if not su_file:
                raise FileNotFoundError("Aucun fichier SU disponible pour suxwigb.")

            wsl_su_file = self.windows_to_wsl_path(su_file)

            command = (
                f"wsl bash -c \"export DISPLAY=192.168.0.23:0; "
                f"export CWPROOT=/usr/local/cwp; "
                f"/usr/local/cwp/bin/suxwigb < {wsl_su_file} title='Wiggle Plot' key=offset fill=1\""
            )

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")

            if process.returncode == 0:
                self.result_text.insert(tk.END, f"Wiggle plot généré avec suxwigb pour : {su_file}\n")
            else:
                raise RuntimeError(f"Erreur dans suwigb : {stderr}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exécuter suxwigb : {e}")



    def run_suximage(self):
        """
        Exécute suximage pour afficher un fichier SU.
        - Si suvelan est exécuté avant, affiche le fichier généré par suvelan.
        - Sinon, affiche le fichier chargé via load_data.
        """
        try:
            su_file = None

            for step in self.workflow:
                if step["module"]["name"] == "suvelan":
                    su_file = getattr(self, "suvelan_output_file", None)

            if not su_file:
                su_file = getattr(self, "su_file", None)

            if not su_file:
                raise FileNotFoundError("Aucun fichier SU disponible pour suximage.")

            wsl_su_file = self.windows_to_wsl_path(su_file)

            command = (
                f"wsl bash -c \"export DISPLAY=192.168.0.23:0; "
                f"export CWPROOT=/usr/local/cwp; "
                f"/usr/local/cwp/bin/suximage < {wsl_su_file} title='Affichage de suximage'\""
            )

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")

            if process.returncode == 0:
                self.result_text.insert(tk.END, f"Fichier affiché avec suximage : {su_file}\n")
            else:
                raise RuntimeError(f"Erreur dans suximage : {stderr}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'exécuter suximage : {e}")



    def close_project(self):
        """
        Ferme le projet en cours, réinitialise les données et le workflow.
        """
        self.stream = None
        self.workflow.clear()
        self.workflow_modules.clear()
        self.workflow_listbox.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.file_label.config(text="Aucun fichier chargé")
        messagebox.showinfo("Projet fermé", "Le projet a été fermé et les données ont été réinitialisées.")



    def on_module_double_click(self, event):
        """
        Gère le double-clic sur un module. Si le module nécessite des paramètres, une fenêtre de saisie s'ouvre.
        Sinon, il est directement ajouté au workflow.
        """
        selected_index = self.module_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            module = self.modules[index]

            if not module["params"]:
                self.workflow.append({"module": module, "params": {}})
                self.workflow_listbox.insert(tk.END, module["name"])
                self.workflow_modules.add(module["name"])
            else:
                self.open_parameter_window(module)




    def open_parameter_window(self, module):
        """
        Ouvre une fenêtre de dialogue pour entrer les paramètres du module sélectionné.
        """
        param_window = tk.Toplevel(self)
        param_window.title(f"Paramètres pour {module['name']}")
        param_window.geometry("300x300")

        param_entries = {}

        for param in module["params"]:
            label = ttk.Label(param_window, text=f"{param}:")
            label.pack(pady=5)
            entry = ttk.Entry(param_window)
            entry.pack(pady=5)
            param_entries[param] = entry

        def on_validate():
            """
            Valide les paramètres saisis pour un module et l'ajoute au workflow.
            """
            try:
                if module["name"] == "suvelan":
                    params_values = {
                        "nv": int(param_entries["nv"].get()),
                        "dv": float(param_entries["dv"].get()),
                        "fv": float(param_entries["fv"].get())
                    }
                    self.workflow.append({"module": module, "params": params_values})
                    self.workflow_listbox.insert(
                        tk.END,
                        f"{module['name']} (nv={params_values['nv']}, dv={params_values['dv']}, fv={params_values['fv']})"
                    )

                elif module["name"] == "sunmo":
                    tnmo = list(map(float, param_entries["tnmo"].get().split(',')))
                    vnmo = list(map(float, param_entries["vnmo"].get().split(',')))

                    if len(tnmo) != len(vnmo):
                        raise ValueError("Le nombre de valeurs tnmo et vnmo doit être égal.")

                    self.workflow.append({"module": module, "params": {"tnmo": tnmo, "vnmo": vnmo}})
                    self.workflow_listbox.insert(tk.END, f"{module['name']} (tnmo={tnmo}, vnmo={vnmo})")


                else:
                    self.workflow.append({"module": module, "params": {}})
                    self.workflow_listbox.insert(tk.END, module["name"])

                self.workflow_modules.add(module["name"])

                param_window.destroy()

            except ValueError as e:
                messagebox.showerror("Erreur", f"Erreur de saisie : {e}")
            except KeyError:
                messagebox.showerror("Erreur", "Paramètres manquants pour le module sélectionné.")

        validate_button = ttk.Button(param_window, text="Valider", command=on_validate)
        validate_button.pack(pady=10)




    def add_external_module(self):
        """
        Permet à l'utilisateur de sélectionner un fichier exécutable (Matlab, C, C++, Python, etc.)
        et l'ajoute au workflow.
        """
        filetypes = [
            ("Matlab Files", "*.m"),
            ("C/C++ Executables", "*.exe;*.out"),
            ("Fortran Executables", "*.f90;*.exe"),
            ("Python Files", "*.py"),
            ("All Files", "*.*")
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)

        if filepath:
            param_window = tk.Toplevel(self)
            param_window.title(f"Paramètres pour {os.path.basename(filepath)}")
            param_window.geometry("300x200")

            param_entries = {}

            label = ttk.Label(param_window, text="Paramètres (séparés par des espaces) :")
            label.pack(pady=5)
            entry = ttk.Entry(param_window)
            entry.pack(pady=5)
            param_entries['params'] = entry

            def on_validate():
                params = entry.get()
                self.workflow.append({"module": filepath, "params": params})
                self.workflow_listbox.insert(tk.END, os.path.basename(filepath))
                param_window.destroy()

            validate_button = ttk.Button(param_window, text="Valider", command=on_validate)
            validate_button.pack(pady=10)

    def run_workflow(self):
        """
        Exécute le workflow en appliquant chaque module ou exécutable sélectionné.
        """
        if not self.workflow:
            messagebox.showerror("Erreur", "Le workflow est vide. Veuillez ajouter des modules.")
            return

        create_script = messagebox.askyesno("Créer un script bash", "Souhaitez-vous générer un script bash pour ce workflow ?")
        script_content = ""

        for step in self.workflow:
            module = step["module"]
            params = step["params"]

            try:
                if module["name"] == "suvelan":
                    nv = params.get("nv")
                    dv = params.get("dv")
                    fv = params.get("fv")
                    if nv is None or dv is None or fv is None:
                        raise ValueError("Paramètres manquants pour suvelan.")
                    self.run_suvelan(int(nv), float(dv), float(fv))
                    command = f"/usr/local/cwp/bin/suvelan < input_file.su nv={nv} dv={dv} fv={fv} > output_suvelan.su"

                elif module["name"] == "sunmo":
                    tnmo = params.get("tnmo")
                    vnmo = params.get("vnmo")
                    if tnmo is None or vnmo is None:
                        raise ValueError("Paramètres manquants pour sunmo.")
                    self.run_sunmo(tnmo, vnmo)
                    command = f"/usr/local/cwp/bin/sunmo < input_file.su tnmo={tnmo} vnmo={vnmo} > output_sunmo.su"


                elif module["name"] == "sustack":
                    self.run_sustack()
                    command = f"/usr/local/cwp/bin/sustack < input_file.su > output_sustack.su"


                elif module["name"] == "suximage":
                    self.run_suximage()
                    command = f"/usr/local/cwp/bin/suximage < input_file.su title='Affichage'"


                elif module["name"] == "suxwigb":
                    self.run_suxwigb()
                    command = f"/usr/local/cwp/bin/suxwigb < input_file.su title='Affichage graphique'"

                elif module["name"] == "surange":
                    self.run_surange()
                    command = f"/usr/local/cwp/bin/surange < input_file.su"

                else:
                    func = module["function"]
                    func(**params)

                self.result_text.insert(tk.END, f"{module['name']} exécuté avec succès.\n")

                if create_script:
                    script_content += command + "\n"

            except Exception as e:
                self.result_text.insert(tk.END, f"Erreur lors de l'exécution de {module['name']} : {e}\n")

        if create_script and script_content:
            try:
                script_path = os.path.join(self.output_dir, "workflow_script.sh")
                with open(script_path, "w") as script_file:
                    script_file.write("#!/bin/bash\n")
                    script_file.write("# Script généré par Sismique GUI\n")
                    script_file.write(script_content)
                self.result_text.insert(tk.END, f"Script bash généré avec succès : {script_path}\n")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer le script bash : {e}")




    def execute_external_module(self, filepath, params):
        """
        Exécute un module externe (Matlab, C, C++, Fortran, Python).
        """
        extension = os.path.splitext(filepath)[1].lower()

        if extension == ".m":
            command = f"matlab -batch \"run('{filepath} {params}')\""
        elif extension in [".exe", ".out"]:
            command = f"{filepath} {params}"
        elif extension == ".py":
            command = f"python {filepath} {params}"
        elif extension in [".f90", ".for", ".exe"]:
            command = f"{filepath} {params}"
        else:
            command = f"{filepath} {params}"

        subprocess.run(command, shell=True)


if __name__ == "__main__":
    app = WorkflowApp()
    app.mainloop()
