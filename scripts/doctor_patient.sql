CREATE TABLE public.doctor_patient
(
    doctor_id integer,
    patient_id integer,
    CONSTRAINT doctor_fkey FOREIGN KEY (doctor_id)
        REFERENCES public.doctor (doctor_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT patient_fkey FOREIGN KEY (patient_id)
        REFERENCES public.patient (patient_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE ,
    CONSTRAINT doctor_patient_unq UNIQUE (doctor_id, patient_id)
);
