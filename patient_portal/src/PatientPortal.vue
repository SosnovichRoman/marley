<template>
	<div class="w-full h-full">
		<div>
			<Tabs as="div" v-model="portal_tabs" :tabs="tabs">
				<template #tab-panel="{ tab }">
					<div v-if="tab.label == 'Appointments'">
						<AppointmentModel />
					</div>
					<div v-else-if="tab.label == 'Visits'">
						<EncounterModel />
					</div>
					<div v-else-if="tab.label == 'Medications'">
						<MedicationModel />
					</div>
					<div v-else-if="tab.label == 'Orders'">
						<OrdersModel />
					</div>
					<div v-else-if="tab.label == 'Medical Record'">
						<MedicalRecord />
					</div>
				</template>
			</Tabs>
		</div>
	</div>

	<Dialog :options="{
		title: dialog_title,
		message: dialog_message,
		size: 'xl',
		icon: {
			name: 'alert-triangle',
			appearance: 'warning',
		},
		actions: [
			{
				label: 'OK',
				variant: 'solid',
			},
		],
	}" v-model="alert_dialog" @click="alert_dialog = false" />
</template>

<script setup>
import { ref, provide } from 'vue'
import AppointmentModel from '@/components/AppointmentModel.vue'
import EncounterModel from '@/components/EncounterModel.vue'
import MedicationModel from '@/components/MedicationModel.vue'
import OrdersModel from '@/components/OrdersModel.vue'
import MedicalRecord from '@/components/MedicalRecord.vue'

import {
	createResource,
	Tabs,
	Dialog,
} from 'frappe-ui'

let alert_dialog = ref(false);

const portal_tabs = ref(0);
const requestedEncounter = ref(null);
const loggedInPatient = ref(null);

let dialog_title = ref("");
let dialog_message = ref("");

let healthcareSettings = ref({});

const tabs = [
	{ label: 'Appointments' },
	{ label: 'Visits' },
	{ label: 'Medications' },
	{ label: 'Orders' },
	{ label: 'Medical Record' },
]

function openVisit(name) {
	requestedEncounter.value = name
	const index = tabs.findIndex((tab) => tab.label === 'Visits')
	if (index >= 0) {
		portal_tabs.value = index
	}
}

provide('openVisit', openVisit)
provide('requestedEncounter', requestedEncounter)
provide('loggedInPatient', loggedInPatient)
provide('healthcareSettings', healthcareSettings)

let getHealthcareSettings = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_settings",
	method: "GET",
	onSuccess(response) {
		if (response) {
			healthcareSettings.value = response
		}
	},
});
getHealthcareSettings.fetch();

let set_logged_in_patient = createResource({
	url: "/api/method/healthcare.healthcare.api.patient_portal.get_logged_in_patient",
	method: "GET",
	onSuccess(response) {
		loggedInPatient.value = response || null
		if (response) {
			localStorage.setItem("patient", JSON.stringify(response));
		}
	},
	onError(error) {
		dialog_message.value = error.messages?.[0] || error;
		dialog_title.value = "Failed to load appointments";
		alert_dialog.value = true;
	}
});
set_logged_in_patient.fetch();

</script>
